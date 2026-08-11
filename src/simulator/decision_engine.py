"""
Moteur de décision simple: décide quelles transformations appliquer selon le fingerprint.
Les règles sont pédagogiques (exemples).
"""

def decide_transformations(fingerprint):
    """
    fingerprint: dict retourné par fingerprint_environment()
    Renvoie une liste d'opérations à appliquer:
      - 'rename_vars', 'obfuscate_strings', 'add_noop'
    """
    ops = []
    # règle simple: si système Linux appliquer obfuscation de chaînes et renommage
    if fingerprint.get("platform_system", "").lower() == "linux":
        ops = ["obfuscate_strings", "rename_vars", "add_noop"]
    else:
        # sinon appliquer seulement renommage et noop
        ops = ["rename_vars", "add_noop"]
    return ops
