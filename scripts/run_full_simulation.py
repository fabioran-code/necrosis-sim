"""
Script d'orchestration complet (safe) :
- crée des stores factices
- exécute le moteur de décision enrichi
- simule l'extraction et l'exfiltration locale (fichiers)
- envoie des logs au MockSIEM et exécute détection
- sauvegarde résultats dans results/ (metrics, logs, images)
"""
from pathlib import Path
import json
import time
import random
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
RESULTS.mkdir(exist_ok=True)

from src.simulator.stores import FakeStores, extract_from_all, pretty_print_extracted
from src.simulator.decision_engine_enhanced import DecisionEngineEnhanced
from src.simulator.siem import MockSIEM


def simulate_full_run(n_targets=3, seed=42):
    random.seed(seed)
    # 1. créer stores factices
    stores = FakeStores()
    stores_summary = {k: len(v) for k, v in [('sam', stores.sam), ('browser', stores.browser), ('app', stores.app), ('network', stores.network)]}

    # 2. obtenir fingerprint léger
    try:
        from src.simulator.fingerprinter import fingerprint_environment
        fp = fingerprint_environment()
    except Exception:
        fp = {'platform_system':'unknown'}

    # 3. décision enrichie
    de = DecisionEngineEnhanced()
    plan = de.plan(fp, stores_summary, budget=10.0)

    # 4. exécution plan (simulation safe)
    siem = MockSIEM()
    all_extracted = {}

    for step in plan:
        action = step['action']
        if action.startswith('extract_'):
            store_name = action.split('_',1)[1]
            policy = {store_name: 0.9}
            extracted = extract_from_all(stores, policy=policy).get(store_name, [])
            # log access attempts
            for acc, cred in extracted:
                siem.ingest({'type':'access','source_host':'host_sim','target_store':store_name,'account':acc})
            all_extracted[store_name] = extracted
        elif action.startswith('exfil'):
            # simulate exfil: write small or large files to results/ (no network)
            size = 128 if action=='exfil_small' else 2048
            fname = RESULTS / f'exfil_{int(time.time())}_{action}.bin'
            with open(fname, 'wb') as f:
                f.write(b'X'*size)
            siem.ingest({'type':'exfil','source_host':'host_sim','size':size,'path':str(fname)})

    # 5. save extracted summary
    summary = {'fingerprint': fp, 'plan': plan, 'extracted_summary': {k: len(v) for k,v in all_extracted.items()}}
    with open(RESULTS / 'simulation_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    # 6. SIEM analysis
    siem.save_logs(str(RESULTS / 'siem_logs.json'))
    alerts = siem.simple_rule_alerts()
    anomalies = siem.anomaly_detection()

    with open(RESULTS / 'siem_analysis.json', 'w', encoding='utf-8') as f:
        json.dump({'alerts': alerts, 'anomalies': anomalies}, f, indent=2)

    # 7. visualisations: bar plot des extractions par store
    stores_names = list(all_extracted.keys())
    counts = [len(all_extracted.get(s, [])) for s in stores_names]
    if stores_names:
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(stores_names, counts)
        ax.set_title('Nombre d\'éléments extraits par store (simulation)')
        ax.set_ylabel('N éléments')
        fig.tight_layout()
        fig.savefig(RESULTS / 'extraction_counts.png', dpi=150)
        plt.close(fig)

    return {
        'summary': str(RESULTS / 'simulation_summary.json'),
        'siem_logs': str(RESULTS / 'siem_logs.json'),
        'siem_analysis': str(RESULTS / 'siem_analysis.json'),
        'extraction_plot': str(RESULTS / 'extraction_counts.png') if stores_names else None
    }

if __name__ == '__main__':
    out = simulate_full_run()
    print('Simulation terminée. Fichiers générés:')
    print(out)
