from ._anvil_designer import z_user_loginTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Mail_valideur  # pour button_export_xls_click


class z_user_login(z_user_loginTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        
    def focus_name(self, **kws):
        """Focus on the password box."""
        self.email_box.focus()       

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('Main')

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        # --------------------------------Tests sur mail
        # mail vide ?
        if self.email_box.text == "":
            alert("Entrez votre mail svp !")
            return
        # mail en minuscule    et strip
        mel = self.email_box.text
        mel = mel.lower()
        mel = mel.strip()
        self.email_box.text = mel

        # @ ds mail ?
        if "@" not in self.email_box.text:
            alert("Entrez un mail valide !")
            self.email_box.focus()
            return
        # --------------------------------Tests sur mot de passe   
        if self.password_box.text == "":
            alert("Entrez le mot de passe svp !")
            self.password_box.focus()
            return   
        # ------------------------------------------------------------   VALIDATION 
        try:
            user=anvil.users.login_with_email(self.email_box.text, self.password_box.text, remember=True)
            user=anvil.server.call("force_log",user)
            open_form('Main',99)    #x=3 si login normal
            #return_to_mother_app.calling_mother_app(99)    #je retourne et efface l'url
        except anvil.users.EmailNotConfirmed:
            alert("Votre mail n'est pas encore confirmé! Nous vous envoyons un nouveau lien par mail !")
            if anvil.server.call('_send_email_confirm_link', self.email_box.text):
                alert(f"Un nouvel email de confirmation vous a été envoyé à {self.email_box.text}.")
                open_form('Main',99)   #je retourne et efface l'url
        except anvil.users.AuthenticationFailed as e:
            #alert(f"Erreur:\n\n{e}")
            alert("Erreur:\n\nAdresse email ou Mot de Passe erroné !")
            return

    def password_box_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_validation_click()

    def reset_pw_link_click(self, **event_args):
        """This method is called when the link is clicked"""
        
        # --------------------------------Tests sur mail
        # mail vide ?
        if self.email_box.text == "":
            alert("Entrez votre mail svp !")
            self.email_box.focus()
            return
            
        # mail en minuscule    et strip
        mel = self.email_box.text
        mel = mel.lower()
        mel = mel.strip()
        self.email_box.text = mel

        # Mail format validation
        result = Mail_valideur.is_valid_email(mel)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            alert("Le mail n'a pas le bon format !")
            self.email_box.focus()
            return

        if anvil.server.call('_send_password_reset', self.email_box.text):
            alert(f"Un mail de réinitilisation du mot de passe vous a été envoyé à {self.email_box.text}.")
            open_form('Main',99)     #je retourne et efface l'url






