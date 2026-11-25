"""Grid Search MaintAI (TP5) : 25 combinaisons, chaque cas = un run MLflow.

À lancer depuis TP\\TP5, environnement activé :  python grid_search.py
Durée : environ 30 s par cas, donc 12 à 15 minutes.
Sorties : grid_results.csv, grid_report.md (section du compte rendu + extrait ADR).
"""
import csv
import inspect
import re
import subprocess
import sys

import mlflow
from mlflow.tracking import MlflowClient

# --- Espace de recherche : 4 x 5 (logreg) + 5 (forest) = 25 cas (<= 30) ---------
GRID_LOGREG = {
    "C": [0.01, 0.1, 1.0, 10.0],             # régularisation : forte -> faible
    "threshold": [0.15, 0.2, 0.3, 0.4, 0.5],  # seuil de décision
}
GRID_FOREST = {
    "threshold": [0.15, 0.2, 0.3, 0.4, 0.5],  # la forêt n'a pas de C : seul le seuil varie
}
PRECISION_MIN = 0.50  # contrainte métier : on tolère des fausses alertes, mais pas plus d'une sur deux
GRID_TAG = "gridsearch-1"

mlflow.set_tracking_uri("sqlite:///mlflow.db")  # même base que celle de mlflow ui (dans TP5)
client = MlflowClient()


def build_cases():
    cases = [
        {"model": "logreg", "C": c, "threshold": t}
        for c in GRID_LOGREG["C"]
        for t in GRID_LOGREG["threshold"]
    ]
    cases += [{"model": "forest", "C": None, "threshold": t} for t in GRID_FOREST["threshold"]]
    return cases


def run_grid(cases):
    """Boucle du Grid Search : un entraînement (donc un run MLflow) par cas."""
    results = []
    for i, case in enumerate(cases, 1):
        cmd = [sys.executable, "-m", "maintai.train",
               "--model", case["model"], "--threshold", str(case["threshold"])]
        if case["C"] is not None:
            cmd += ["--C", str(case["C"])]
        print(f"[{i}/{len(cases)}] {' '.join(cmd[2:])}", flush=True)
        out = subprocess.run(cmd, capture_output=True, text=True)
        found = re.search(r"Run MLflow\s*:\s*([0-9a-f]+)", out.stdout)
        if not found:
            print("   échec :", out.stderr[-300:])
            continue
        run_id = found.group(1)
        client.set_tag(run_id, "grid", GRID_TAG)
        data = client.get_run(run_id).data
        results.append({**case, "run_id": run_id,
                        "data_md5": data.params.get("data_md5", ""),
                        "n_train": data.params.get("n_train", ""),
                        "recall": data.metrics["recall"],
                        "precision": data.metrics["precision"],
                        "accuracy": data.metrics["accuracy"]})
    return results


def f2(p, r):
    return 5 * p * r / (4 * p + r) if (4 * p + r) else 0.0


def fmt(c):
    return "—" if c is None else f"{c:g}"


def main():
    cases = build_cases()
    assert len(cases) <= 30, "trop de cas"
    results = run_grid(cases)
    for r in results:
        r["f2"] = f2(r["precision"], r["recall"])

    with open("grid_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    # Sélection : recall maximal parmi les cas qui respectent la contrainte de précision
    admissibles = [r for r in results if r["precision"] >= PRECISION_MIN]
    classement = sorted(admissibles, key=lambda r: (r["recall"], r["f2"]), reverse=True)
    best = classement[0]
    top5 = classement[:5]

    L = []
    L.append("## Grid Search\n")
    L.append("### Espace de recherche\n")
    L.append("| Hyperparamètre | Marge de variation | Valeurs testées |")
    L.append("|---|---|---|")
    L.append("| `model` | 2 modèles | `logreg`, `forest` |")
    L.append(f"| `C` (logreg seulement) | de 0.01 (forte régularisation) à 10 (faible), échelle logarithmique | {GRID_LOGREG['C']} |")
    L.append(f"| `threshold` | de 0.15 (très sensible) à 0.5 (seuil neutre) | {GRID_LOGREG['threshold']} |")
    L.append(f"\nTotal : {len(GRID_LOGREG['C'])} × {len(GRID_LOGREG['threshold'])} (logreg) + "
             f"{len(GRID_FOREST['threshold'])} (forest) = **{len(cases)} cas** (maximum autorisé : 30). "
             f"Tous les runs portent le tag MLflow `grid = {GRID_TAG}` et ont été entraînés sur les mêmes données "
             f"(`data_md5` = `{best['data_md5'][:8]}`).\n")
    L.append("### Code de la boucle\n")
    L.append("```python\n" + inspect.getsource(run_grid).rstrip() + "\n```\n")
    L.append(f"### Résultats détaillés : les 5 meilleurs runs (précision ≥ {PRECISION_MIN})\n")
    L.append("| Rang | model | C | threshold | recall | precision | accuracy | F2 | run_id |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for k, r in enumerate(top5, 1):
        L.append(f"| {k} | {r['model']} | {fmt(r['C'])} | {r['threshold']:g} | {r['recall']:.3f} | "
                 f"{r['precision']:.3f} | {r['accuracy']:.3f} | {r['f2']:.3f} | `{r['run_id'][:8]}` |")
    L.append(f"\nLes {len(cases)} cas sont dans `grid_results.csv` ; {len(results) - len(admissibles)} d'entre eux "
             f"sont écartés car leur précision est sous {PRECISION_MIN}.\n")
    L.append("### Meilleure combinaison\n")
    L.append(f"Critère : recall maximal (une panne manquée coûte plus cher qu'une fausse alerte), sous la contrainte "
             f"precision ≥ {PRECISION_MIN} pour ne pas noyer les techniciens sous les fausses alertes. "
             f"Retenu : **{best['model']}, C = {fmt(best['C'])}, threshold = {best['threshold']:g}** "
             f"(recall {best['recall']:.3f}, precision {best['precision']:.3f}, accuracy {best['accuracy']:.3f}).\n")
    L.append("---\n")
    L.append("## À reporter dans `docs/adr/004-choix-du-modele.md`\n")
    L.append(f"- **Décision** : modèle `{best['model']}`, C = {fmt(best['C'])}, seuil de décision {best['threshold']:g}.")
    L.append(f"- **Run MLflow** : `{best['run_id']}`")
    L.append(f"- **data_md5** : `{best['data_md5']}`")
    L.append(f"- **Contrainte** : une panne manquée coûte plus cher qu'une fausse alerte, donc on maximise le recall, "
             f"avec une précision plancher de {PRECISION_MIN}.")
    L.append(f"- **Justification** : sur {len(results)} cas, c'est le meilleur recall ({best['recall']:.3f}) "
             f"parmi les {len(admissibles)} cas admissibles ; precision {best['precision']:.3f}, accuracy {best['accuracy']:.3f}.")
    L.append("- **Ce que l'on accepte en échange** : plus de fausses alertes qu'avec un seuil de 0.5 "
             "(compléter avec l'écart de precision observé dans votre tableau).")
    L.append("- **Limite** : seuil et hyperparamètres choisis sur le jeu de test, donc le recall est un peu optimiste ; "
             "la taille du jeu de test laisse une incertitude de plusieurs points.")

    with open("grid_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\nTerminé : grid_results.csv et grid_report.md créés.")


if __name__ == "__main__":
    main()