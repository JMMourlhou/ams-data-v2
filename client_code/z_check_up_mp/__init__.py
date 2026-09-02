from ._anvil_designer import z_check_up_mpTemplate
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class z_check_up_mp(z_check_up_mpTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        temporary_password = self.text_box_temporary_password.text

        users_found = anvil.server.call("users_with_temporary_password", temporary_password)
        
        print(f"{len(users_found)} utilisateur(s) trouvé(s)")
        
        for user_found in users_found:
            print(
                user_found["email"],
                user_found["nom"],
                user_found["prenom"],
                user_found["role"]
            )