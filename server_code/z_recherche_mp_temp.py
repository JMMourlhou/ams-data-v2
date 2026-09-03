import bcrypt
import anvil.server
from anvil.tables import app_tables
import anvil.tables as tables


@anvil.server.background_task
def search_users_with_temp_pword(temporary_password):
    """
    Recherche en arrière-plan les utilisateurs utilisant encore
    le mot de passe temporaire.

    Cette fonction ne modifie aucune donnée.
    """

    temporary_password_bytes = temporary_password.encode("utf-8")

    users_found = []

    users_list = list(app_tables.users.search())
    total_users = len(users_list)

    for user_number, user_row in enumerate(users_list, start=1):
        stored_password_hash = user_row["password_hash"]

        if stored_password_hash is not None:

            if isinstance(stored_password_hash, str):
                stored_password_hash = stored_password_hash.encode("utf-8")

            try:
                password_matches = bcrypt.checkpw(
                    temporary_password_bytes,
                    stored_password_hash
                )
            except (ValueError, TypeError):
                password_matches = False

            if password_matches:
                users_found.append({
                    "email": user_row["email"],
                    "nom": user_row["nom"],
                    "prenom": user_row["prenom"],
                    "role": user_row["role"],
                })

        # Informations récupérables depuis le client
        anvil.server.task_state["current_user"] = user_number
        anvil.server.task_state["total_users"] = total_users
        anvil.server.task_state["users_found"] = len(users_found)

    anvil.server.task_state["finished"] = True

    # en fin de task, on retourne la valeur (après la commande 'return')
    # Cette valeur est récupérée par le timer de la BG task par:  users_found_list = self.task.get_return_value()
    return users_found

@anvil.server.callable
def users_with_temporary_password(temporary_password):
    connected_user = anvil.users.get_user()
    print(f"Server side: {connected_user['nom']} {connected_user['prenom']} / role: {connected_user['role']}")

    if connected_user is None:
        raise anvil.server.PermissionDenied("Utilisateur non connecté.")
        return
    if connected_user["role"] != "A":
        raise anvil.server.PermissionDenied("Accès réservé à l'administrateur.")
        return
    task = anvil.server.launch_background_task('search_users_with_temp_pword',temporary_password)
    
    # Renvoi de la task avec ses Informations récupérables depuis le client
    return task
    