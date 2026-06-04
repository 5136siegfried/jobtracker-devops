from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import date, datetime, timedelta
from collections import Counter
import os
import json
import calendar

from models import db, User, Candidature

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me-in-prod")
    default_db = "sqlite:///" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "jobtracker.db"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.login_message = "Connecte-toi pour accéder au tracker."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        # Migration douce : ajouter colonne theme si absente
        from sqlalchemy import text, inspect
        insp = inspect(db.engine)
        cols = [c["name"] for c in insp.get_columns("users")]
        if "theme" not in cols:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN theme VARCHAR(20) DEFAULT 'cyber'"))
                conn.commit()

    # ─── AUTH ──────────────────────────────────────────────────────────────────

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                return redirect(url_for("dashboard"))
            flash("Identifiants incorrects.", "error")
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if not username or not password:
                flash("Champs obligatoires.", "error")
            elif User.query.filter_by(username=username).first():
                flash("Ce nom d'utilisateur est déjà pris.", "error")
            elif len(password) < 6:
                flash("Mot de passe trop court (6 caractères min).", "error")
            else:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash("Compte créé !", "success")
                return redirect(url_for("dashboard"))
        return render_template("register.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # ─── THEME ─────────────────────────────────────────────────────────────────

    @app.route("/api/theme", methods=["POST"])
    @login_required
    def set_theme():
        data = request.get_json()
        theme = data.get("theme", "cyber")
        if theme not in ("cyber", "zen", "kirby"):
            return jsonify({"error": "Invalid theme"}), 400
        current_user.theme = theme
        db.session.commit()
        return jsonify({"ok": True, "theme": theme})

    # ─── DASHBOARD ─────────────────────────────────────────────────────────────

    @app.route("/")
    @login_required
    def dashboard():
        candidatures = Candidature.query.filter_by(user_id=current_user.id)\
            .order_by(Candidature.date_candidature.desc()).all()

        today = date.today()
        monday = today - timedelta(days=today.weekday())
        cette_semaine = [c for c in candidatures if c.date_candidature >= monday]

        OBJECTIF_HEBDO = 5
        progress = min(int((len(cette_semaine) / OBJECTIF_HEBDO) * 100), 100)

        etat_counter = Counter(c.etat for c in candidatures)
        urgentes = [c for c in candidatures if c.deadline_urgente and c.etat not in ("refuse", "accepte")]
        depassees = [c for c in candidatures if c.deadline_depassee and c.etat not in ("refuse", "accepte")]

        stats = {
            "total": len(candidatures),
            "en_attente": etat_counter.get("en_attente", 0),
            "entretiens": sum(v for k, v in etat_counter.items() if "entretien" in k),
            "cette_semaine": len(cette_semaine),
            "objectif_hebdo": OBJECTIF_HEBDO,
            "progress": progress,
            "etats": dict(etat_counter),
            "urgentes": len(urgentes),
            "depassees": len(depassees),
        }

        return render_template("dashboard.html",
            candidatures=candidatures[:5],
            stats=stats,
            urgentes=urgentes,
            today=today,
        )

    # ─── CALENDRIER ────────────────────────────────────────────────────────────

    @app.route("/calendar")
    @login_required
    def cal():
        today = date.today()
        year  = int(request.args.get("year",  today.year))
        month = int(request.args.get("month", today.month))

        # Navigation
        prev_month = date(year, month, 1) - timedelta(days=1)
        next_month = date(year, month, 1) + timedelta(days=32)
        next_month = date(next_month.year, next_month.month, 1)

        # Tous les events du mois
        month_start = date(year, month, 1)
        last_day    = calendar.monthrange(year, month)[1]
        month_end   = date(year, month, last_day)

        candidatures = Candidature.query.filter_by(user_id=current_user.id).all()

        events = []  # {date, label, type, cid}
        for c in candidatures:
            if c.prochaine_deadline and month_start <= c.prochaine_deadline <= month_end:
                events.append({
                    "date": c.prochaine_deadline,
                    "label": f"⏰ {c.entreprise}",
                    "type": "deadline",
                    "cid": c.id,
                    "overdue": c.deadline_depassee,
                    "urgent": c.deadline_urgente,
                })
            if c.date_candidature and month_start <= c.date_candidature <= month_end:
                events.append({
                    "date": c.date_candidature,
                    "label": f"✉ {c.entreprise}",
                    "type": "candidature",
                    "cid": c.id,
                    "overdue": False,
                    "urgent": False,
                })

        # Grille calendrier : semaines
        cal_matrix = calendar.monthcalendar(year, month)

        # Events indexés par jour
        events_by_day = {}
        for e in events:
            d = e["date"].day
            events_by_day.setdefault(d, []).append(e)

        # Events triés pour la vue liste (tout le futur/présent)
        upcoming = sorted(
            [e for e in events if e["date"] >= today],
            key=lambda x: x["date"]
        )

        return render_template("calendar.html",
            year=year, month=month,
            month_name=calendar.month_name[month],
            cal_matrix=cal_matrix,
            events_by_day=events_by_day,
            upcoming=upcoming,
            prev=prev_month,
            next=next_month,
            today=today,
        )

    # ─── TUTORIEL ──────────────────────────────────────────────────────────────

    @app.route("/tutorial")
    @login_required
    def tutorial():
        return render_template("tutorial.html")

    # ─── LIST ──────────────────────────────────────────────────────────────────

    @app.route("/list")
    @login_required
    def list_candidatures():
        etat_filter    = request.args.get("etat", "")
        contrat_filter = request.args.get("contrat", "")
        sort           = request.args.get("sort", "date_desc")

        q = Candidature.query.filter_by(user_id=current_user.id)
        if etat_filter:
            q = q.filter_by(etat=etat_filter)
        if contrat_filter:
            q = q.filter_by(type_contrat=contrat_filter)

        sort_map = {
            "date_desc":  Candidature.date_candidature.desc(),
            "date_asc":   Candidature.date_candidature.asc(),
            "score_desc": Candidature.niveau_interet.desc(),
            "entreprise": Candidature.entreprise.asc(),
        }
        q = q.order_by(sort_map.get(sort, Candidature.date_candidature.desc()))
        candidatures = q.all()

        etats    = ["en_attente","attente_reponse","entretien_planifie",
                    "entretien_realise","test_technique","offre_recue","accepte","refuse","ghosted"]
        contrats = ["CDI","CDD","Freelance","Stage","Alternance"]

        return render_template("list.html",
            candidatures=candidatures,
            etats=etats, contrats=contrats,
            etat_filter=etat_filter,
            contrat_filter=contrat_filter,
            sort=sort,
        )

    # ─── FORM ADD / EDIT ───────────────────────────────────────────────────────

    @app.route("/form", methods=["GET", "POST"])
    @login_required
    def form():
        if request.method == "POST":
            def get_int(key, default=3):
                try: return int(request.form.get(key, default))
                except: return default
            def parse_date(key):
                val = request.form.get(key, "")
                try: return datetime.strptime(val, "%Y-%m-%d").date() if val else None
                except: return None

            c = Candidature(
                user_id=current_user.id,
                entreprise=request.form.get("entreprise","").strip(),
                poste=request.form.get("poste","").strip(),
                date_candidature=parse_date("date_candidature") or date.today(),
                prochaine_deadline=parse_date("prochaine_deadline"),
                type_contrat=request.form.get("type_contrat",""),
                teletravail=request.form.get("teletravail",""),
                salaire_min=get_int("salaire_min",0),
                salaire_max=get_int("salaire_max",0),
                niveau_interet=get_int("niveau_interet"),
                contact_nom=request.form.get("contact_nom",""),
                contact_email=request.form.get("contact_email",""),
                niveau_tech=get_int("niveau_tech"),
                ambiance_valeurs=get_int("ambiance_valeurs"),
                ethique=get_int("ethique"),
                remuneration=get_int("remuneration"),
                evolution=get_int("evolution"),
                reputation_pro=get_int("reputation_pro"),
                ressenti=request.form.get("ressenti",""),
                notes=request.form.get("notes",""),
                etat="en_attente",
            )
            db.session.add(c)
            db.session.commit()
            flash(f"Candidature {c.entreprise} ajoutée.", "success")
            return redirect(url_for("dashboard"))

        return render_template("form.html", today=date.today())

    @app.route("/candidature/<int:cid>/edit", methods=["GET","POST"])
    @login_required
    def edit(cid):
        c = Candidature.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
        if request.method == "POST":
            def get_int(key, default=3):
                try: return int(request.form.get(key, default))
                except: return default
            def parse_date(key):
                val = request.form.get(key,"")
                try: return datetime.strptime(val,"%Y-%m-%d").date() if val else None
                except: return None

            c.entreprise        = request.form.get("entreprise", c.entreprise).strip()
            c.poste             = request.form.get("poste", c.poste).strip()
            c.prochaine_deadline= parse_date("prochaine_deadline")
            c.type_contrat      = request.form.get("type_contrat", c.type_contrat)
            c.teletravail       = request.form.get("teletravail", c.teletravail)
            c.salaire_min       = get_int("salaire_min", c.salaire_min)
            c.salaire_max       = get_int("salaire_max", c.salaire_max)
            c.niveau_interet    = get_int("niveau_interet", c.niveau_interet)
            c.contact_nom       = request.form.get("contact_nom", c.contact_nom)
            c.contact_email     = request.form.get("contact_email", c.contact_email)
            c.niveau_tech       = get_int("niveau_tech", c.niveau_tech)
            c.ambiance_valeurs  = get_int("ambiance_valeurs", c.ambiance_valeurs)
            c.ethique           = get_int("ethique", c.ethique)
            c.remuneration      = get_int("remuneration", c.remuneration)
            c.evolution         = get_int("evolution", c.evolution)
            c.reputation_pro    = get_int("reputation_pro", c.reputation_pro)
            c.ressenti          = request.form.get("ressenti", c.ressenti)
            c.notes             = request.form.get("notes", c.notes)
            c.etat              = request.form.get("etat", c.etat)
            db.session.commit()
            flash("Candidature mise à jour.", "success")
            return redirect(url_for("detail", cid=c.id))

        etats = ["en_attente","attente_reponse","entretien_planifie",
                 "entretien_realise","test_technique","offre_recue","accepte","refuse","ghosted"]
        return render_template("form.html", today=date.today(), c=c, etats=etats)

    # ─── API ───────────────────────────────────────────────────────────────────

    @app.route("/api/candidature/<int:cid>/etat", methods=["PATCH"])
    @login_required
    def update_etat(cid):
        c = Candidature.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
        data = request.get_json()
        new_etat = data.get("etat","")
        etats_valides = ["en_attente","attente_reponse","entretien_planifie",
                         "entretien_realise","test_technique","offre_recue",
                         "accepte","refuse","ghosted"]
        if new_etat not in etats_valides:
            return jsonify({"error": "État invalide"}), 400
        c.etat = new_etat
        db.session.commit()
        return jsonify({"ok": True, "etat": c.etat})

    # ─── DETAIL / DELETE ───────────────────────────────────────────────────────

    @app.route("/candidature/<int:cid>")
    @login_required
    def detail(cid):
        c = Candidature.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
        return render_template("detail.html", c=c)

    @app.route("/candidature/<int:cid>/delete", methods=["POST"])
    @login_required
    def delete(cid):
        c = Candidature.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
        db.session.delete(c)
        db.session.commit()
        flash(f"Candidature {c.entreprise} supprimée.", "success")
        return redirect(url_for("list_candidatures"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8001)
