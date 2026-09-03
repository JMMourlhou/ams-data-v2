from ._anvil_designer import z_check_up_mpTemplate
import anvil
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
from ..AlertConfirmHTML import AlertConfirmHTML

class z_check_up_mp(z_check_up_mpTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        


    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        temporary_password = self.text_box_temporary_password.text
        if len(temporary_password) == 0:
            alert("Entrez un Mp")
            self.text_box_temporary_password.focus()
            return
            
        if self.check_box_raz.checked is True:
            r = AlertConfirmHTML.ask(
                "RAZ des Mp :",
                "<p>Voulez-vous forcer les users à Réinitialiser leur MP ?</p>",
                style="error",
                large = True
            )
            if not r :   # non
                return
                
        alert("Les users concernés seront visibles en logs")
        self.label_progress.visible = True
        self.task = anvil.server.call("users_with_temporary_password", temporary_password, self.check_box_raz.checked)


    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if not hasattr(self, "task"):
            return

        # récupère le dictionaire maj en BG task
        state = self.task.get_state()
        current_user = state.get("current_user", 0)
        total_users = state.get("total_users", 0)
        users_found = state.get("users_found", 0)
    
        self.label_progress.text = (
            f"{current_user}/{total_users} utilisateurs contrôlés "
            f"- {users_found} trouvé(s)"
        )

        # Si task achevée, on récupère la liste des users identifiés
        if state.get("finished"):
            self.timer_1.interval = 0
    
            users_found_list = self.task.get_return_value()
    
            print("")
            print(f"{len(users_found_list)} utilisateur(s) trouvé(s)")
    
            for user_found in users_found_list:
                print(f'{user_found["email"]}, {user_found["nom"]}, {user_found["prenom"]}, role: {user_found["role"]}')

                
    def check_box_raz_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        pass  # Write Code Here


        
