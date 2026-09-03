import bcrypt
import anvil.server
from anvil.tables import app_tables
import anvil.tables as tables


@anvil.server.background_task
def users_with_temp_pword(temporary_password, require_user=True):
    """
    Recherche les utilisateurs qui utilisent encore le mot de passe temporaire.

    Entrée :
        temporary_password : mot de passe temporaire à rechercher.

    Sortie :
        liste des utilisateurs concernés.

    Cette fonction ne modifie aucune donnée.
    """
    
    

    users_found = []

    for user_row in app_tables.users.search(
        tables.order_by("nom", ascending=True)
    ):
        print(f"{user_row['nom']}")
        stored_password_hash = user_row["password_hash"]

        if stored_password_hash is None:
            continue

        # bcrypt.checkpw attend des bytes.
        if isinstance(stored_password_hash, str):
            stored_password_hash = stored_password_hash.encode("utf-8")

        temporary_password_bytes = temporary_password.encode("utf-8")

        try:
            password_matches = bcrypt.checkpw(temporary_password_bytes, stored_password_hash)
        except (ValueError, TypeError):
            password_matches = False

        if password_matches:
            print(f'PW matching: {user_row["email"]}, {user_row["nom"]}, {user_row["prenom"]}, role: {user_row["role"]}, confirmé: {user_row["confirmed_email"]}')
            users_found.append({
                "email": user_row["email"],
                "nom": user_row["nom"],
                "prenom": user_row["prenom"],
                "role": user_row["role"],
                "confirmed_email": user_row["confirmed_email"],
            })


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
    task = anvil.server.launch_background_task('users_with_temp_pword',temporary_password)
    return task
    