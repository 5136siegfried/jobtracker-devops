# 🧪 jobtracker-devops

![Build](https://img.shields.io/badge/build-manual-blue)
![State](https://img.shields.io/badge/state-beta-important)
![License](https://img.shields.io/badge/license-MIT-green)
![DevOps](https://img.shields.io/badge/IaC-YAML-informational)
![Pipeline](https://img.shields.io/badge/pipeline-human--driven-ff69b4)
![Status](https://img.shields.io/badge/mood-slightly%20overqualified-yellow)
![Coffee](https://img.shields.io/badge/caffeine-∞mg-black)

```bash
       __        __   ______                    __
      / /____   / /_ /_  __/_____ ____ _ _____ / /__ ___   _____
 __  / // __ \ / __ \ / /  / ___// __ `// ___// //_// _ \ / ___/
/ /_/ // /_/ // /_/ // /  / /   / /_/ // /__ / ,<  /  __// /
\____/ \____//_.___//_/  /_/    \__,_/ \___//_/|_| \___//_/

   🧠  Tu as des chasseurs de tête aux baskets mon chum ?
          → T'es au bon endroit. On versionne nos refus. Prépare ta GLACE.
```

╔═════════════════════════════════════════════╗
║        jobtracker-devops (YAML FTW)         ║
╠═════════════════════════════════════════════╣
║  • track • compare • plan • version • win   ║
╚═════════════════════════════════════════════╝

Un pipeline Git pour suivre tes candidatures comme un vrai ingénieur SRE : versionné, lisible, scoré, et potentiellement observable en prod (si tu trouves un CDI avant).

> 📁 "Candidatures.yaml or die trying."

---

## 📌 Pourquoi ce repo ?

Parce qu’un fichier Excel, c’est bien... jusqu’à ce que tu sois DevOps.
Ici, tu déclares tes candidatures comme une stack Kubernetes : propre, modulaire, et documentée.

---

## 🚀 Features

- 🔎 **Suivi YAML-first** : entreprise, poste, contacts, intérêt, critères éthiques, deadlines, etc.
- 🗓️ **Agenda intégré** : entretiens, relances, décisions critiques (avec café).
- 📊 **Comparateur d’offres** : multicritère (tech, valeurs, $$$, vibe).
- 📁 **Pool documentaire** : CV, lettres, portfolios… le tout linké.
- 🤖 **Ready for GPT scraping** (bientôt) : parsing automatique d’offres.
- 🧬 **Modulaire** : versionnable, diffable, diffusable.
- 🕶️ **Ne tracke pas ta vie, juste ton avenir.**

---

## 🧱 Structure du dépôt

```bash
jobtracker-devops/
├── candidates.sample.yaml       # Ton fichier de démo safe pour la prod publique
├── .gitignore                   # Ton vrai YAML est en local (privacy FTW)
├── scripts/
│   ├── generate_dashboard.py    # À venir : Markdown / HTML dashboard
├── docs/
│   ├── CV_DevOps_Sample.pdf     # Exemples fictifs
├── README.md
├── LICENSE (MIT)
```

```bash
$ ./scripts/apply.sh
> applying to all jobs in candidates.yaml...
> error: human interaction required
```

---

### 🧬 3. **Graph Mermaid.js**

Dans le README ou une page à part :

```markdown
```mermaid
flowchart LR
  A[Repéré une offre] --> B[Ajout YAML]
  B --> C[Évaluation multi-critères]
  C --> D{Entretien ?}
  D -->|Oui| E[Agenda updated]
  D -->|Non| F[Relance automatisée]
  E --> G[Comparaison]
  F --> G
  G --> H[Décision finale]
  H --> I[Git commit --sign-off]

---

### 🔁 4. **Alias Git custom pour brag**
Dans une section « Dev Setup » :

```bash
alias jobpush='git add . && git commit -m "feat(job): update pipeline" && git push'
alias refreshbrain='caffeine.sh && clear && echo "Remember: you are the pipeline."'
```
