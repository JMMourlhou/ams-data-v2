from ._anvil_designer import z_user_pw_resetTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. AlertHTML import AlertHTML

class z_user_pw_reset(z_user_pw_resetTemplate):
    def __init__(self,email, api_key, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.password_box.text = ""
        self.password_repeat_box.text = ""
        self.email = email
        self.api_key = api_key

    def focus_password(self, **kws):
        """Focus on the password box."""
        self.password_box.focus()

    def button_validation_click(self, **event_args):
        """Validation et modification du nouveau mot de passe."""
    
        # Premier mot de passe vide ?
        if self.password_box.text == "":
            AlertHTML.info(
                "Oubli :",
                "Entrez votre Mot de Passe !"
            )
            self.password_box.focus()
            return
    
        # Confirmation vide ?
        if self.password_repeat_box.text == "":
            AlertHTML.info(
                "Oubli :",
                "Entrez votre Mot de Passe une deuxième fois !"
            )
            self.password_repeat_box.focus()
            return
    
        # Longueur minimale
        if len(self.password_box.text) < 6:
            AlertHTML.info(
                "Mot de Passe :",
                "Utilisez au minimum 6 caractères."
            )
            self.password_box.focus()
            return
    
        # Les deux mots de passe doivent être identiques
        if self.password_box.text != self.password_repeat_box.text:
            AlertHTML.error(
                "Erreur :",
                "Les Mots de Passe sont différents !"
            )
    
            self.password_repeat_box.text = ""
            self.password_repeat_box.focus()
            return
    
        # Validation définitive côté serveur
        result = anvil.server.call(
            "_perform_password_reset",
            self.email,
            self.api_key,
            self.password_box.text
        )
    
        if result:
            AlertHTML.success(
                "Succès !",
                "Vous pouvez vous connecter avec le nouveau Mot de Passe !"
            )
    
            self.button_retour_click()
            return
    
        AlertHTML.error(
            "Erreur :",
            "Ce lien de réinitialisation est invalide ou a expiré.",
            "Le lien dure 30 min !"
        )

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('Main',99)     #je retourne et efface l'url