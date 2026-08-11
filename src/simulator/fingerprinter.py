"""
Module de fingerprinting (collecte d'informations non sensibles)
Ne collecte QUE des métadonnées non sensibles (OS, version Python, variables d'environnement non privées).
"""
import platform
import sys
import os

def fingerprint_environment():
    """Retourne un dict minimalisant les informations sensibles."""
    info = {
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "executable": os.path.basename(sys.executable),
        # variables d'environnement non sensibles (filtrées)
        "env_keys_sample": list(os.environ.keys())[:10],  # uniquement les clés, pas les valeurs
    }
    return info
