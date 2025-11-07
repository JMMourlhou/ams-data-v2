import anvil.server
import datetime
from . import French_zone_server_side
_sessions = {}

@anvil.server.callable
def register_session(session_id):
    # insertion ds ledico des sessions
    _sessions[session_id] = French_zone_server_side.time_french_zone()
    print(f"Nouvelle session enregistrée : {session_id}")
    print(f"Nb total de session enregistrées : {len(_sessions)}")

@anvil.server.callable
def unregister_session(session_id):
    if session_id in _sessions:
        del _sessions[session_id]
        print(f"Session {session_id} fermée.")
        print(f"Nb total de session enregistrées : {len(_sessions)}")