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
        """This method is called when the button is clicked"""
        if self.password_box.text == "":
            alert("Entrez un mot de passe !")
            return
        if self.password_repeat_box.text == "":
            alert("Entrez 2 fois le mot de passe !")
            return         
        # si 2 pass words identiques
        if self.password_box.text == self.password_repeat_box.text:
            r=anvil.server.call("_perform_password_reset",self.email, self.api_key, self.password_box.text)
            if r:
                alert("Vous pouvez vous connecter avec le nouveau mot de passe !")
                self.button_retour_click()
        else:
            alert("Les mots de passe sont différents !")
            return

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('Main',99)     #je retourne et efface l'url