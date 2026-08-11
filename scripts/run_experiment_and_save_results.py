#!/usr/bin/env python3
"""
Lance une expérience toy, sauvegarde features / metrics / figures dans results/
Usage:
  python scripts/run_experiment_and_save_results.py
"""
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# setup paths
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXAMPLES = ROOT / "examples" / "benign_scripts"
RESULTS.mkdir(exist_ok=True)

# importer le simulateur (assure-toi que src/ est sur le path)
import sys
sys.path.insert(0, str(ROOT / "src"))
from simulator.fingerprinter import fingerprint_environment
from simulator.decision_engine import decide_transformations
from simulator.mutator import Mutator

def extract_features(source_text):
    return {
        "n_lines": len(source_text.splitlines()),
        "n_imports": source_text.count("import "),
        "n_base64": source_text.count("b64decode"),
        "n_noop": source_text.count("_noop_extra_"),
    }

def run_experiment(n_mutants=20, test_size=0.4, random_state=42):
    print("Démarrage de l'expérience (toy).")
    fp = fingerprint_environment()
    ops = decide_transformations(fp)
    print("Fingerprint:", fp)
    print("Transformations décidées:", ops)

    src_file = EXAMPLES / "sample_script.py"
    with open(src_file, "r", encoding="utf-8") as f:
        src = f.read()

    # dataset: 1 original + n_mutants mutés
    variants = []
    labels = []
    variants.append(src)
    labels.append(0)
    for i in range(n_mutants):
        m = Mutator(ops)
        mutated = m.mutate_source(src)
        variants.append(mutated)
        labels.append(1)

    # extract features
    df = pd.DataFrame([extract_features(v) for v in variants])
    df["label"] = labels

    # save features
    features_path = RESULTS / "features.csv"
    df.to_csv(features_path, index=False)
    print(f"Features saved to {features_path}")

    # training simple
    X = df.drop(columns=["label"])
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    clf = LogisticRegression(max_iter=200)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # metrics
    report = classification_report(y_test, y_pred, output_dict=False)
    cm = confusion_matrix(y_test, y_pred)
    metrics = {
        "accuracy": float(clf.score(X_test, y_test)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "feature_means_original": X[y==0].mean().to_dict(),
        "feature_means_mutated": X[y==1].mean().to_dict(),
    }
    # save classification report
    cr_path = RESULTS / "classification_report.txt"
    with open(cr_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Classification report saved to {cr_path}")

    # save metrics json
    metrics_path = RESULTS / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")

    # confusion matrix plot
    fig_cm, ax = plt.subplots(figsize=(4,4))
    im = ax.imshow(cm, cmap='Blues')
    ax.set_title("Matrice de confusion")
    ax.set_xlabel("Prédit")
    ax.set_ylabel("Vrai")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="black")
    fig_cm.tight_layout()
    cm_path = RESULTS / "confusion_matrix.png"
    fig_cm.savefig(cm_path, dpi=150)
    plt.close(fig_cm)
    print(f"Confusion matrix image saved to {cm_path}")

    # feature means bar plot
    means = pd.DataFrame({
        "original": metrics["feature_means_original"],
        "mutated": metrics["feature_means_mutated"]
    })
    fig_f, ax = plt.subplots(figsize=(6,4))
    means.plot.bar(ax=ax)
    ax.set_title("Moyennes des features (original vs muté)")
    ax.set_ylabel("Valeur moyenne")
    fig_f.tight_layout()
    fm_path = RESULTS / "feature_means.png"
    fig_f.savefig(fm_path, dpi=150)
    plt.close(fig_f)
    print(f"Feature means image saved to {fm_path}")

    print("Expérience terminée.")
    return {
        "features_csv": str(features_path),
        "metrics_json": str(metrics_path),
        "classification_report": str(cr_path),
        "confusion_matrix_png": str(cm_path),
        "feature_means_png": str(fm_path),
    }

if __name__ == "__main__":
    run_experiment()
