"""
Fake credential stores and safe simulated extraction routines.
All operations are synthetic and do NOT access real system stores.
Used to simulate SAM, browser, application and network credential sources.
"""
from typing import Dict, List, Tuple
import random
import json

class FakeStores:
    def __init__(self):
        # Each store is a dict mapping "account" -> "credential" (synthetic)
        self.sam = {"ADMIN$": "P@ssw0rd_admin", "svc_backup": "backup!23"}
        self.browser = {"alice@example.com": "cookie_alice_abc123", "bob@example.com": "cookie_bob_xyz"}
        self.app = {"svc_db": "db_token_987", "web_app_user": "webpwd123"}
        self.network = {"ssh_host_1": "ssh_key_1", "ssh_host_2": "ssh_key_2"}

    def list_stores(self) -> Dict[str, List[str]]:
        return {
            "sam": list(self.sam.keys()),
            "browser": list(self.browser.keys()),
            "app": list(self.app.keys()),
            "network": list(self.network.keys()),
        }

def simulate_extraction(store: Dict[str,str], strength: float=0.8) -> List[Tuple[str,str]]:
    """
    Simule l'extraction d'éléments depuis un store fictif.
    strength : probabilité moyenne de succès par élément (0..1)
    Retourne la liste d'items extraits (account, credential)
    """
    extracted = []
    for acc, cred in store.items():
        if random.random() < strength:
            # retourner l'item (on ne fait pas d'opérations réelles)
            extracted.append((acc, cred))
    return extracted

def extract_from_all(stores: FakeStores, policy: Dict[str,float]=None) -> Dict[str,List[Tuple[str,str]]]:
    """
    Applique une politique d'extraction (probabilités par store) et retourne un dict des éléments extraits.
    policy ex: {"sam":0.9, "browser":0.6, ...}
    """
    if policy is None:
        policy = {"sam":0.7, "browser":0.6, "app":0.6, "network":0.5}
    res = {}
    res["sam"] = simulate_extraction(stores.sam, policy.get("sam", 0.6))
    res["browser"] = simulate_extraction(stores.browser, policy.get("browser", 0.6))
    res["app"] = simulate_extraction(stores.app, policy.get("app", 0.6))
    res["network"] = simulate_extraction(stores.network, policy.get("network", 0.6))
    return res

def pretty_print_extracted(extracted: Dict[str,List[Tuple[str,str]]]) -> str:
    lines = []
    for k, items in extracted.items():
        lines.append(f"Store {k}: {len(items)} éléments extraits")
        for acc, cred in items:
            lines.append(f"  - {acc}: {cred}")
    return "\n".join(lines)

if __name__ == "__main__":
    # petit test
    stores = FakeStores()
    ext = extract_from_all(stores)
    print(pretty_print_extracted(ext))
