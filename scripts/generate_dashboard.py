import yaml
import argparse
from tabulate import tabulate
from pathlib import Path

def load_candidates(path="candidates.yaml"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("candidatures", [])
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {path}")
        return []

def display_table(candidats):
    table = []
    for c in candidats:
        table.append([
            c.get("entreprise", ""),
            c.get("poste", ""),
            c.get("etat", ""),
            c.get("niveau_interet", ""),
            c.get("prochaine_deadline", "")
        ])
    print(tabulate(table, headers=["Entreprise", "Poste", "État", "Intérêt", "Deadline"], tablefmt="github"))

def compare(candidats, ent1, ent2):
    c1 = next((c for c in candidats if c["entreprise"].lower() == ent1.lower()), None)
    c2 = next((c for c in candidats if c["entreprise"].lower() == ent2.lower()), None)

    if not c1 or not c2:
        print(f"❌ Impossible de trouver : {ent1 if not c1 else ''} {ent2 if not c2 else ''}")
        return

    criteria = [
        "niveau_tech",
        "ambiance_valeurs",
        "ethique",
        "remuneration",
        "evolution",
        "reputation_pro",
        "ressenti"
    ]

    table = []
    for crit in criteria:
        val1 = c1.get("evaluation", {}).get(crit, "-")
        val2 = c2.get("evaluation", {}).get(crit, "-")
        table.append([crit, val1, val2])

    print(f"\n🔍 Comparaison entre **{c1['entreprise']}** et **{c2['entreprise']}**\n")
    print(tabulate(table, headers=["Critère", c1["entreprise"], c2["entreprise"]], tablefmt="fancy_grid"))

def main():
    parser = argparse.ArgumentParser(description="📊 Jobtracker Dashboard Generator")
    parser.add_argument("--compare", nargs=2, metavar=("ENTREPRISE1", "ENTREPRISE2"), help="Compare deux entreprises")
    args = parser.parse_args()

    path = Path("candidates.yaml")
    if not path.exists():
        print("🔎 Aucun fichier `candidates.yaml` trouvé. Utilisation de `candidates.sample.yaml`.")
        path = Path("candidates.sample.yaml")

    candidats = load_candidates(path)

    if args.compare:
        compare(candidats, args.compare[0], args.compare[1])
    else:
        display_table(candidats)

if __name__ == "__main__":
    main()
