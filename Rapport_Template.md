# Rapport Template

Ce template est utilisé par tools/generate_report.py pour insérer les métriques et images générées lors de l'exécution des expériences.

Placeholders remplacés automatiquement :
- {{ACCURACY}} : accuracy du classifieur
- {{N_TRAIN}} / {{N_TEST}} : tailles train/test
- {{CLASSIFICATION_REPORT}} : rapport de classification (texte)
- {{CONFUSION_MATRIX_IMG}} : image PNG matrice de confusion
- {{FEATURE_MEANS_IMG}} : image PNG moyennes des features
- {{METRICS_JSON}} : dump JSON des métriques
