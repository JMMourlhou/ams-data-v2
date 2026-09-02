import bcrypt
import anvil.server
from anvil.tables import app_tables


@anvil.server.callable(require_user=True)
def users_with_temporary_password(temporary_password):
    """
    Recherche les utilisateurs qui utilisent encore le mot de passe temporaire.

    Entrée :
        temporary_password : mot de passe temporaire à rechercher.

    Sortie :
        liste des utilisateurs concernés.

    Cette fonction ne modifie aucune donnée.
    """

    connected_user = anvil.users.get_user()

    if connected_user is None:
        raise anvil.server.PermissionDenied("Utilisateur non connecté.")

    if connected_user["role"] != "A":
        raise anvil.server.PermissionDenied("Accès réservé à l'administrateur.")

    users_found = []

    for user_row in app_tables.users.search():
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
            users_found.append({
                "email": user_row["email"],
                "nom": user_row["nom"],
                "prenom": user_row["prenom"],
                "role": user_row["role"],
                "confirmed_email": user_row["confirmed_email"],
            })

    return users_found