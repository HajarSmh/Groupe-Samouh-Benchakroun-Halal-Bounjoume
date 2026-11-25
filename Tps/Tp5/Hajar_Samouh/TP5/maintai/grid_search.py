"""Grid search MaintAI : 30 combinaisons, chaque run est enregistré dans MLflow."""
import csv
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

from maintai.tracking import file_md5

DATA = Path("data/sensors.csv")
MIN_PRECISION = 0.50  # critère fixé AVANT de voir les résultats
C_VALUES = [0.01, 0.1, 1.0, 10.0]
THRESHOLDS = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4]

GRID = [("logreg", c, t) for c, t in itertools.product(C_VALUES, THRESHOLDS)]
GRID += [("forest", None, t) for t in THRESHOLDS]
assert len(GRID) <= 30, len(GRID)

rows = []
for i, (model, c, t) in enumerate(GRID, 1):
    cmd = [sys.executable, "-m", "maintai.train", "--model", model, "--threshold", str(t)]
    if c is not None:
        cmd += ["--C", str(c)]
    out = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if out.returncode != 0:
        print(f"[{i}/{len(GRID)}] ECHEC {cmd}\n{out.stderr[-500:]}")
        continue
    m = json.loads(re.search(r'\{\s*"model".*?\n\}', out.stdout, re.S).group(0))["model"]
    run_id = re.search(r"Run MLflow : (\w+)", out.stdout).group(1)
    p, r = m["precision"], m["recall"]
    f2 = 5 * p * r / (4 * p + r) if (4 * p + r) else 0.0
    rows.append({"model": model, "C": c, "threshold": t, "recall": r,
                 "precision": p, "accuracy": m["accuracy"], "f2": round(f2, 3),
                 "run_id": run_id})
    print(f"[{i}/{len(GRID)}] {model} C={c} seuil={t} recall={r} precision={p}")

with open("grid_results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

# Critère : recall maximal avec precision >= MIN_PRECISION (une panne manquée coûte plus cher)
ok = [r for r in rows if r["precision"] >= MIN_PRECISION]
ok.sort(key=lambda r: (r["recall"], r["precision"]), reverse=True)

print(f"\ndata_md5 = {file_md5(DATA)}")
print(f"{len(ok)} cas sur {len(rows)} respectent precision >= {MIN_PRECISION}\n")
print("| Rang | model | C | seuil | recall | precision | accuracy | F2 | run_id |")
print("|---|---|---|---|---|---|---|---|---|")
for k, r in enumerate(ok[:5], 1):
    print(f"| {k} | {r['model']} | {r['C']} | {r['threshold']} | {r['recall']} | "
          f"{r['precision']} | {r['accuracy']} | {r['f2']} | {r['run_id']} |")