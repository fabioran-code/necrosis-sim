Ajout: stores factices, mock-SIEM, moteur de décision enrichi et script d'orchestration.

Fichiers nouveaux:
- src/simulator/stores.py
- src/simulator/siem.py
- src/simulator/decision_engine_enhanced.py
- scripts/run_full_simulation.py

Usage:
1) Activer venv et installer dépendances
2) python scripts/run_full_simulation.py
Le script produit des fichiers sous results/ (simulation_summary.json, siem_logs.json, siem_analysis.json, extraction_counts.png)
