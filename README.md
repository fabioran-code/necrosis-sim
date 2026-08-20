# Projet NECROSIS 
Objectif : Modéliser et simuler, à des fins pédagogiques et défensives, les techniques d'un "malware caméléon" . Le dépôt fournit un simulateur qui transforme des scripts Python bénins pour étudier l'effet des mutations sur la détection.

Important — règles de sécurité et éthique
- Tous les fichiers manipulés sont fournis dans `examples/` ou générés localement.
- Ne pas exécuter le projet sur des machines de production ; utiliser une machine d'étude ou VM isolée.
- Ne pas importer ou exécuter d'échantillons malveillants externes.

Structure du dépôt
- examples/ : scripts Python bénins (entrées)
- src/simulator/ : modules (fingerprinter, decision engine, mutator)
- notebooks/ : notebook d'exemple (format .py Jupytext)
- scripts/ : scripts d'orchestration (run_demo.py)
- requirements.txt : dépendances

Prérequis
- Python 3.9+ (utilisation d'`ast.unparse`)
- Installer les dépendances : pip install -r requirements.txt

Utilisation rapide
1. Cloner / créer le dépôt et copier les fichiers.
2. Installer dépendances.
3. Lancer :
   python scripts/run_demo.py
