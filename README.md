# JobTracker DevOps

Outil de suivi de candidatures/alternances/freelance — multi-profils, self-hosted.

## Stack

```
Flask 3.1 + SQLAlchemy + SQLite
Flask-Login (sessions)
Werkzeug (hash passwords)
Docker (image ~150MB)
```

## Lancement rapide

```bash
# Dev local
pip install -r requirements.txt
cd app
python app.py

# Production Docker
docker compose up -d

# Avec clé secrète custom
SECRET_KEY=votre-cle-ici docker compose up -d
```

# User et password
```bash
# User
cd jobtracker/app
python -c "
from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    users = User.query.all()
    print([u.username for u in users])
"
# password
cd jobtracker/app
python -c "
from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    u = User.query.filter_by(username='sieg').first()
    u.set_password('nouveau_mdp')
    db.session.commit()
    print('Done')
"
```

## Déploiement VPS (nginx + Docker)

```nginx
# /etc/nginx/sites-available/jobtracker
server {
    server_name jobtracker.yourdomain.com;
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
certbot --nginx -d jobtracker.yourdomain.com
```

## Backup DB

```bash
# Backup manuel
docker exec jobtracker sqlite3 /data/jobtracker.db .dump > backup_$(date +%Y%m%d).sql

# Ou rsync du volume
rsync -avz /var/lib/docker/volumes/jobtracker_jobtracker_data/ ./backups/
```

## Features

- Auth multi-users (login/register, passwords hashés bcrypt)
- Dashboard : stats, objectif hebdo, alertes deadline
- Candidatures : CRUD complet, filtres, tri
- Mise à jour état **inline sans rechargement** (AJAX PATCH)
- Badges deadline urgente (⚡ <48h) et dépassée (⚠)
- Score global calculé (moyenne 6 critères)
- Detail page avec barres de scores visuelles
- Style cyberpunk dark cohérent (Share Tech Mono + Exo 2)

## Crédits

Créé par [Siegfried Sekkai](https://github.com/5136Siegfried) — 5136.fr
