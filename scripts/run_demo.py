"""
Script d'orchestration démonstration (inoffensif).
- lit examples/benign_scripts/sample_script.py
- collecte fingerprint (non sensible)
- décide transformations
- génère une version mutée dans examples/benign_scripts/mutated_sample.py
- extrait quelques features et affiche résultats simples
"""
import os
from src.simulator import fingerprint_environment, decide_transformations, Mutator
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    print("DEMO: simulateur pédagogique NECROSIS (version sûre)")
    fp = fingerprint_environment()
    print("Fingerprint (extrait) :", fp)
    ops = decide_transformations(fp)
    print("Transformations décidées :", ops)

    src_path = ROOT / "examples" / "benign_scripts" / "sample_script.py"
    dst_path = ROOT / "examples" / "benign_scripts" / "mutated_sample.py"

    with open(src_path, "r", encoding="utf-8") as f:
        src = f.read()

    mutator = Mutator(ops)
    mutated = mutator.mutate_source(src)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write("# Fichier muté (généré par Mutator)\n")
        f.write(mutated)

    print(f"Mutated file written to: {dst_path}")
    # quelques features simples
    n_lines = len(mutated.splitlines())
    n_base64 = mutated.count("b64decode")
    print(f"Features: lignes={n_lines}, nombre_chaine_obfusquee={n_base64}")
    print("Fin de la démo. Ouvre notebooks/simulation_example.py pour un notebook détaillé.")

if __name__ == "__main__":
    main()
