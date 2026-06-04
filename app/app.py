from flask import Flask, render_template, request, redirect
import yaml
from datetime import date, datetime, timedelta
from collections import Counter


app = Flask(__name__)
DATA_FILE = "candidates.yaml"

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "GET":
        return render_template("form.html", today=date.today())
    if request.method == "POST":
        new_entry = {
              "entreprise": request.form["entreprise"],
              "poste": request.form["poste"],
              "date_candidature": request.form["date_candidature"],
              "niveau_interet": int(request.form["niveau_interet"]),
              "etat": "en_attente",
              "contact": {
                  "nom": request.form.get("contact_nom", ""),
                  "email": request.form.get("contact_email", "")
              },
              "type_contrat": request.form.get("type_contrat", ""),
              "teletravail": request.form.get("teletravail", ""),
              "salaire_k": {
                  "min": int(request.form.get("salaire_min", 0)),
                  "max": int(request.form.get("salaire_max", 0))
              },
              "evaluation": {
                  "niveau_tech": int(request.form["niveau_tech"]),
                  "ambiance_valeurs": int(request.form["ambiance_valeurs"]),
                  "ethique": int(request.form["ethique"]),
                  "remuneration": int(request.form["remuneration"]),
                  "evolution": int(request.form["evolution"]),
                  "reputation_pro": int(request.form["reputation_pro"]),
                  "ressenti": request.form["ressenti"]
              },
              "prochaine_deadline": request.form["prochaine_deadline"]
        }
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except FileNotFoundError:
            data = {}

        data.setdefault("candidatures", []).append(new_entry)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

        return redirect("/")

@app.route("/list")
def list_candidatures():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {}

    candidatures = data.get("candidatures", [])
    return render_template("list.html", candidatures=candidatures)

@app.route("/")
def dashboard():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {}

    candidatures = data.get("candidatures", [])
    documents = data.get("pool_documents", [])
    notes = data.get("notes", [])
    agenda = data.get("agenda", [])

    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    this_week = [
        c for c in candidatures
        if c.get("date_candidature") and c["date_candidature"]
    ]

    OBJECTIF_HEBDO = 5
    progress = int((len(this_week) / OBJECTIF_HEBDO) * 100)
    progress = min(progress, 100)

    etat_counter = Counter(c.get("etat", "inconnu") for c in candidatures)
    stats = {
        "total": len(candidatures),
        "en_attente": etat_counter.get("en_attente", 0),
        "entretien": sum(v for k, v in etat_counter.items() if "entretien" in k),
        "cette_semaine": len(this_week),
        "objectif_hebdo": OBJECTIF_HEBDO,
        "progress": progress,
        "etats": dict(etat_counter)
    }

    return render_template("dashboard.html",
        candidatures=candidatures,
        documents=documents,
        notes=notes,
        agenda=agenda,
        stats=stats
    )
# 👇 Le server doit démarrer *après* toutes les routes
if __name__ == "__main__":
    app.run(debug=True)
