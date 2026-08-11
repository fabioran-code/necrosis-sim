"""
Mock SIEM ingestion and anomaly detection (safe, local simulation).
- stocke des logs factices
- applique heuristiques simples et un modèle d'anomalie (IsolationForest) pour détecter événements suspects
"""
from typing import List, Dict, Any
import time
import json
import numpy as np
from sklearn.ensemble import IsolationForest

class MockSIEM:
    def __init__(self):
        self.logs: List[Dict[str,Any]] = []

    def ingest(self, log: Dict[str,Any]):
        log_entry = dict(log)
        if 'timestamp' not in log_entry:
            log_entry['timestamp'] = time.time()
        self.logs.append(log_entry)

    def save_logs(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2)

    def simple_rule_alerts(self) -> List[Dict[str,Any]]:
        """Règles heuristiques: exfil > seuil, trop de tentatives d'accès, etc."""
        alerts = []
        # exemple: si un hôte a plus de 3 exfil events en fenêtre
        counts = {}
        for l in self.logs:
            if l.get('type') == 'exfil':
                host = l.get('source_host', 'unknown')
                counts[host] = counts.get(host, 0) + 1
        for host, c in counts.items():
            if c > 3:
                alerts.append({"host": host, "reason": "trop_d_exfil", "count": c})
        return alerts

    def anomaly_detection(self) -> Dict[str,Any]:
        """Utilise IsolationForest sur features simples: nombre d'exfil, taille cumulée, nombre accès"""
        # construire tableau features par host
        hosts = {}
        for l in self.logs:
            h = l.get('source_host','unknown')
            entry = hosts.setdefault(h, {'n_exfil':0, 'bytes_exfil':0, 'n_access':0})
            if l.get('type') == 'exfil':
                entry['n_exfil'] += 1
                entry['bytes_exfil'] += int(l.get('size',0))
            if l.get('type') == 'access':
                entry['n_access'] += 1
        if not hosts:
            return {'n_hosts':0, 'anomalies':[]} 
        X = np.array([[v['n_exfil'], v['bytes_exfil'], v['n_access']] for v in hosts.values()], dtype=float)
        # si trop peu d'hôtes, on renvoie vide
        if X.shape[0] < 2:
            return {'n_hosts': X.shape[0], 'anomalies': []}
        clf = IsolationForest(random_state=42, contamination=0.1)
        preds = clf.fit_predict(X)
        anomalies = []
        for (host, p) in zip(hosts.keys(), preds):
            if p == -1:
                anomalies.append({'host': host, 'score': float(p)})
        return {'n_hosts': X.shape[0], 'anomalies': anomalies}

if __name__ == "__main__":
    siem = MockSIEM()
    siem.ingest({'type':'exfil','source_host':'hostA','size':1024})
    siem.ingest({'type':'exfil','source_host':'hostA','size':2048})
    siem.ingest({'type':'access','source_host':'hostB'})
    print(siem.simple_rule_alerts())
    print(siem.anomaly_detection())
