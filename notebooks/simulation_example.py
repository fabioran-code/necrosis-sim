# Notebook/Jupyter (format .py) — expérience pédagogique complète
# ------------------------------------------------------------------------------
# Cell 1 - Import et setup
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
from simulator.fingerprinter import fingerprint_environment
from simulator.decision_engine import decide_transformations
from simulator.mutator import Mutator
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Cell 2 - Fingerprint et décision
fp = fingerprint_environment()
print("Fingerprint:", fp)
ops = decide_transformations(fp)
print("Ops:", ops)

# Cell 3 - Générer dataset: plusieurs variantes mutées d'un script bénin
examples_dir = ROOT / "examples" / "benign_scripts"
src_file = examples_dir / "sample_script.py"
with open(src_file, "r", encoding="utf-8") as f:
    src = f.read()

variants = []
labels = []
# original
variants.append(src)
labels.append(0)
# générer 5 variantes mutées
for i in range(5):
    m = Mutator(ops)
    mutated = m.mutate_source(src)
    variants.append(mutated)
    labels.append(1)

# Cell 4 - extraction de features simples
def extract_features(source_text):
    return {
        "n_lines": len(source_text.splitlines()),
        "n_imports": source_text.count("import "),
        "n_base64": source_text.count("b64decode"),
        "n_noop": source_text.count("_noop_extra_"),
    }

df = pd.DataFrame([extract_features(v) for v in variants])
df["label"] = labels
print(df)

# Cell 5 - entraînement d'un classifieur simple
X = df.drop(columns=["label"])
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
clf = LogisticRegression()
clf.fit(X_train, y_train)
pred = clf.predict(X_test)
print(classification_report(y_test, pred))

# Cell 6 - visualisation
plt.figure(figsize=(6,4))
plt.bar(X.columns, X.mean())
plt.title("Moyennes des features (toy example)")
plt.show()

# Fin du notebook
print("Notebook terminé. Interprète ces résultats comme un exemple pédagogique.")
