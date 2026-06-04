from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    theme = db.Column(db.String(20), default="cyber")
    candidatures = db.relationship("Candidature", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Candidature(db.Model):
    __tablename__ = "candidatures"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    entreprise = db.Column(db.String(200), nullable=False)
    poste = db.Column(db.String(200), nullable=False)
    date_candidature = db.Column(db.Date, default=date.today)
    prochaine_deadline = db.Column(db.Date, nullable=True)
    type_contrat = db.Column(db.String(50), default="")
    teletravail = db.Column(db.String(50), default="")
    salaire_min = db.Column(db.Integer, default=0)
    salaire_max = db.Column(db.Integer, default=0)
    niveau_interet = db.Column(db.Integer, default=3)

    contact_nom = db.Column(db.String(200), default="")
    contact_email = db.Column(db.String(200), default="")

    etat = db.Column(db.String(50), default="en_attente")

    niveau_tech = db.Column(db.Integer, default=3)
    ambiance_valeurs = db.Column(db.Integer, default=3)
    ethique = db.Column(db.Integer, default=3)
    remuneration = db.Column(db.Integer, default=3)
    evolution = db.Column(db.Integer, default=3)
    reputation_pro = db.Column(db.Integer, default=3)
    ressenti = db.Column(db.Text, default="")
    notes = db.Column(db.Text, default="")

    @property
    def score_global(self):
        return round((
            self.niveau_tech + self.ambiance_valeurs + self.ethique +
            self.remuneration + self.evolution + self.reputation_pro
        ) / 6, 1)

    @property
    def deadline_depassee(self):
        if self.prochaine_deadline:
            return self.prochaine_deadline < date.today()
        return False

    @property
    def deadline_urgente(self):
        if self.prochaine_deadline:
            delta = (self.prochaine_deadline - date.today()).days
            return 0 <= delta <= 2
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "entreprise": self.entreprise,
            "poste": self.poste,
            "date_candidature": str(self.date_candidature),
            "prochaine_deadline": str(self.prochaine_deadline) if self.prochaine_deadline else None,
            "type_contrat": self.type_contrat,
            "teletravail": self.teletravail,
            "etat": self.etat,
            "score_global": self.score_global,
            "deadline_depassee": self.deadline_depassee,
            "deadline_urgente": self.deadline_urgente,
        }
