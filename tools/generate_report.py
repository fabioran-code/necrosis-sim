#!/usr/bin/env python3
"""
Génère le rapport final Markdown en insérant les métriques et figures produites.
Usage:
  python tools/generate_report.py --results results --template Rapport_Template.md --output Rapport_Projet_NECROSIS_final.md
"""
import argparse
import json
from pathlib import Path

def load_text(path):
    return Path(path).read_text(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Dossier contenant results/ (metrics.json, images, classification_report.txt)")
    parser.add_argument("--template", required=True, help="Chemin vers le template Rapport_Template.md")
    parser.add_argument("--output", required=True, help="Chemin du rapport final à générer (.md)")
    args = parser.parse_args()

    results_dir = Path(args.results)
    template = Path(args.template)
    out = Path(args.output)

    if not results_dir.exists():
        raise SystemExit(f"Le dossier {results_dir} n'existe pas. Exécute d'abord scripts/run_experiment_and_save_results.py")

    metrics_path = results_dir / "metrics.json"
    cr_path = results_dir / "classification_report.txt"
    cm_png = results_dir / "confusion_matrix.png"
    fm_png = results_dir / "feature_means.png"

    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    cr_text = cr_path.read_text(encoding="utf-8") if cr_path.exists() else "No classification report found."

    tpl = template.read_text(encoding="utf-8")

    # remplacements simples
    tpl = tpl.replace("{{ACCURACY}}", f"{metrics.get('accuracy', 'N/A')}")
    tpl = tpl.replace("{{N_TRAIN}}", f"{metrics.get('n_train', 'N/A')}")
    tpl = tpl.replace("{{N_TEST}}", f"{metrics.get('n_test', 'N/A')}")
    # insert classification report as code block
    tpl = tpl.replace("{{CLASSIFICATION_REPORT}}", "```\n" + cr_text + "\n```")

    # insert image markdown (paths relative)
    if cm_png.exists():
        tpl = tpl.replace("{{CONFUSION_MATRIX_IMG}}", f"![Matrice de confusion]({cm_png.as_posix()})")
    else:
        tpl = tpl.replace("{{CONFUSION_MATRIX_IMG}}", "_Image non trouvée_")

    if fm_png.exists():
        tpl = tpl.replace("{{FEATURE_MEANS_IMG}}", f"![Moyennes des features]({fm_png.as_posix()})")
    else:
        tpl = tpl.replace("{{FEATURE_MEANS_IMG}}", "_Image non trouvée_")

    # include metrics JSON pretty (optionnel)
    tpl = tpl.replace("{{METRICS_JSON}}", "```json\n" + json.dumps(metrics, indent=2, ensure_ascii=False) + "\n```")

    out.write_text(tpl, encoding="utf-8")
    print(f"Rapport généré: {out.resolve()}")

if __name__ == "__main__":
    main()
