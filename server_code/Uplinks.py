import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server

# Uplink: Pi5 appel ce module pour extraire les images de la table users
#   et mettre à jour les img des users du Pi5 
@anvil.server.callable
def get_media_data_from_table(user_email):
    row = app_tables.users.get(email=user_email)
    if row and row['image']:
        media = row['image']
        return {
            "id": row.get_id(),
            "bytes": media.get_bytes(),
            "name": media.name,
            "content_type": media.content_type
        }
    return None

