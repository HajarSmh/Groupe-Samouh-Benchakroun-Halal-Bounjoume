"""Grid search MaintAI : un entraînement par combinaison, chacun enregistré comme run MLflow."""
import csv
import itertools
import json
import os
import subprocess
import sys

C_VALUES = [0.01, 0.1, 1.0, 10.0]
THRESHOLDS = [0.15, 0.2, 0.3, 0.4, 0.5]

combinaisons = [("logreg", c, t) for c, t in itertools.product(C_VALUES, THRESHOLDS)]
combinaisons += [("forest", None, t) for t in THRESHOLDS]
assert len(combinaisons) <= 30

env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
resultats = []

for i, (model, c, t) in enumerate(combinaisons, 1):
    cmd = [sys.executable, "-m", "maintai.train", "--model", model, "--threshold", str(t)]
    if c is not None:
        cmd += ["--C", str(c)]
    print(f"[{i}/{len(combinaisons)}] model={model} C={c} threshold={t}", flush=True)

    sortie = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                            env=env, check=True).stdout
    metriques = json.loads(sortie[sortie.index("{"):sortie.rindex("}") + 1])["model"]
    run_id = sortie.split("Run MLflow :")[-1].strip()

    resultats.append({
        "model": model, "C": c if c is not None else "-", "threshold": t,
        "recall": metriques["recall"], "precision": metriques["precision"],
        "accuracy": metriques["accuracy"], "run_id": run_id,
    })

with open("grid_results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=resultats[0].keys())
    w.writeheader()
    w.writerows(resultats)

# Règle de choix : le meilleur recall, avec une precision d'au moins 0.5
candidats = [r for r in resultats if r["precision"] >= 0.5] or resultats
meilleur = max(candidats, key=lambda r: (r["recall"], r["precision"]))

print("\nRésultats triés par recall :")
for r in sorted(resultats, key=lambda r: (r["recall"], r["precision"]), reverse=True):
    print(f"{r['model']:7} C={str(r['C']):5} seuil={r['threshold']:<5} "
          f"recall={r['recall']:.3f} precision={r['precision']:.3f} "
          f"accuracy={r['accuracy']:.3f} run={r['run_id']}")
print(f"\nMeilleure combinaison : {meilleur}")