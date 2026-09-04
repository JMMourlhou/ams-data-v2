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
        self.task = None
        self.timer_1.interval = 0
        
    def button_1_click(self, **event_args):
        """Lance la recherche du mot de passe temporaire."""

        temporary_password = self.text_box_temporary_password.text
    
        if len(temporary_password) == 0:
            alert("Entrez un Mp")
            self.text_box_temporary_password.focus()
            return
    
        if self.check_box_raz.checked is True:
            r = AlertConfirmHTML.ask(
                "RAZ des Mp :",
                "<p>Les MP des utilisateurs ayant ce MP seront remis à None:</p>"
                "<p>Voulez-vous ainsi forcer les users à Réinitialiser leur MP ?</p>",
                style="error",
                large=True
            )
    
            if not r:
                return
    
        alert("Les users concernés seront visibles en logs")
    
        # Préparation de l'affichage
        self.label_progress.text = "Démarrage de la recherche..."
        self.label_progress.visible = True
    
        # Création de la nouvelle Background Task
        self.task = anvil.server.call(
            "users_with_temporary_password",
            temporary_password,
            self.check_box_raz.checked
        )
    
        # Le Timer ne démarre qu'une fois la nouvelle tâche créée
        self.timer_1.interval = 0.5


    def timer_1_tick(self, **event_args):
        """Suit l'avancement de la Background Task."""
    
        if self.task is None:
            return
    
        # Récupération de l'état de la Background Task
        state = self.task.get_state()
    
        current_user = state.get("current_user", 0)
        total_users = state.get("total_users", 0)
        users_found = state.get("users_found", 0)
    
        self.label_progress.text = (
            f"{current_user}/{total_users} utilisateurs contrôlés "
            f"- {users_found} trouvé(s)"
        )
    
        # Background Task terminée
        if state.get("finished"):
            self.timer_1.interval = 0
    
            users_found_list = self.task.get_return_value()
    
            print("")
            print(f"{len(users_found_list)} utilisateur(s) trouvé(s)")
    
            for user_found in users_found_list:
                print(
                    f'{user_found["email"]}, '
                    f'{user_found["nom"]}, '
                    f'{user_found["prenom"]}, '
                    f'role: {user_found["role"]}'
                )
    
            # on oublie l'ancienne task
            self.task = None

                
    def check_box_raz_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        pass  # Write Code Here


    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)



        
