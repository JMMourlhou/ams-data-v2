import anvil.server
from datetime import datetime

# Dictionnaire en mémoire des sessions actives
sessions_actives = {}
"""
@anvil.server.session_lifecycle("connect")
def on_connect(session_id):
    sessions_actives[session_id] = datetime.now()
    print(f"✅ Nouvelle connexion : {session_id} à {sessions_actives[session_id]}")

@anvil.server.session_lifecycle("disconnect")
def on_disconnect(session_id):
    if session_id in sessions_actives:
        del sessions_actives[session_id]
    print(f"❌ Déconnexion : {session_id}")

# Module principal à appelé pour connaitre l'état des connections / sessions actives
@anvil.server.callable
def get_sessions_actives():
    # Permet d’interroger la liste depuis mon interface d’admin / param
    return list(sessions_actives.keys())
"""