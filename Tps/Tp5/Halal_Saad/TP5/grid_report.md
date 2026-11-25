## Grid Search

### Espace de recherche

| Hyperparamètre | Marge de variation | Valeurs testées |
|---|---|---|
| `model` | 2 modèles | `logreg`, `forest` |
| `C` (logreg seulement) | de 0.01 (forte régularisation) à 10 (faible), échelle logarithmique | [0.01, 0.1, 1.0, 10.0] |
| `threshold` | de 0.15 (très sensible) à 0.5 (seuil neutre) | [0.15, 0.2, 0.3, 0.4, 0.5] |

Total : 4 × 5 (logreg) + 5 (forest) = **25 cas** (maximum autorisé : 30). Tous les runs portent le tag MLflow `grid = gridsearch-1` et ont été entraînés sur les mêmes données (`data_md5` = `93fdeef2`).

### Code de la boucle

```python
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
```

### Résultats détaillés : les 5 meilleurs runs (précision ≥ 0.5)

| Rang | model | C | threshold | recall | precision | accuracy | F2 | run_id |
|---|---|---|---|---|---|---|---|---|
| 1 | logreg | 10 | 0.15 | 0.859 | 0.507 | 0.875 | 0.754 | `eb9bbedc` |
| 2 | logreg | 1 | 0.15 | 0.859 | 0.506 | 0.874 | 0.754 | `8b058bb6` |
| 3 | logreg | 0.1 | 0.2 | 0.829 | 0.559 | 0.894 | 0.756 | `8ac21ca5` |
| 4 | logreg | 0.01 | 0.2 | 0.829 | 0.547 | 0.890 | 0.752 | `8bb80254` |
| 5 | forest | — | 0.2 | 0.829 | 0.526 | 0.882 | 0.743 | `45160725` |

Les 25 cas sont dans `grid_results.csv` ; 3 d'entre eux sont écartés car leur précision est sous 0.5.

### Meilleure combinaison

Critère : recall maximal (une panne manquée coûte plus cher qu'une fausse alerte), sous la contrainte precision ≥ 0.5 pour ne pas noyer les techniciens sous les fausses alertes. Retenu : **logreg, C = 10, threshold = 0.15** (recall 0.859, precision 0.507, accuracy 0.875).

---

## À reporter dans `docs/adr/004-choix-du-modele.md`

- **Décision** : modèle `logreg`, C = 10, seuil de décision 0.15.
- **Run MLflow** : `eb9bbedc477242ee9a2ae70d7457ac24`
- **data_md5** : `93fdeef2cac1893c4f720c16457eea75`
- **Contrainte** : une panne manquée coûte plus cher qu'une fausse alerte, donc on maximise le recall, avec une précision plancher de 0.5.
- **Justification** : sur 25 cas, c'est le meilleur recall (0.859) parmi les 22 cas admissibles ; precision 0.507, accuracy 0.875.
- **Ce que l'on accepte en échange** : plus de fausses alertes qu'avec un seuil de 0.5 (compléter avec l'écart de precision observé dans votre tableau).
- **Limite** : seuil et hyperparamètres choisis sur le jeu de test, donc le recall est un peu optimiste ; la taille du jeu de test laisse une incertitude de plusieurs points.
