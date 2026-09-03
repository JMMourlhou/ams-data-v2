from ._anvil_designer import z_user_loginTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Mail_valideur  # pour button_export_xls_click
from .. AlertHTML import AlertHTML

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


        """
        # En cas d'erreur (effact du mp admin), voir :  z_user_modules
        result = anvil.server.call("temporary_restore_admin_password")
        print(result)
        """


        
        
        """This method is called when the button is clicked"""
        # --------------------------------Tests sur mail
        # mail vide ?
        if self.email_box.text == "":
            AlertHTML.info("Oublie :", "Entrez votre mail !")
            return
        # mail en minuscule    et strip
        mel = self.email_box.text
        mel = mel.lower()
        mel = mel.strip()
        self.email_box.text = mel

        # Mail format validation
        result = Mail_valideur.is_valid_email(mel)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            AlertHTML.error("Adresse Mail :", "Mail erroné !")
            self.email_box.focus()
            return
            
        # Tests sur mot de passe   
        if self.password_box.text == "":
            AlertHTML.info("Oublie :", "Entrez votre Mot de Passe !")
            self.password_box.focus()
            return   
        # ------------------------------------------------------------   VALIDATION 
        try:
            user = anvil.users.login_with_email(self.email_box.text, self.password_box.text, remember=True)
            open_form("Main", 99)
        
        except anvil.users.EmailNotConfirmed:
            AlertHTML.info("Adresse mail non confirmée :", "Votre adresse mail n'est pas encore confirmée. Nous vous envoyons un nouveau lien de confirmation.")
        
            if anvil.server.call("_send_email_confirm_link", self.email_box.text):
                AlertHTML.info("Confirmation de votre mail :", f"Un nouvel email de confirmation a été envoyé à {self.email_box.text}.")
        
        except anvil.users.TooManyPasswordFailures:
            AlertHTML.error("Connexion bloquée :", "Trop de tentatives de connexion ont échoué. Utilisez « Mot de passe oublié » pour réinitialiser votre mot de passe.")
            self.password_box.text = ""
            self.password_box.focus()
            
        except anvil.users.AuthenticationFailed:
            #AlertHTML.error("Erreur :", "Email ou Mot de Passe erroné !")
            alert("Email ou Mot de Passe erroné !")
            self.password_box.text = ""
            self.password_box.focus()

    def reset_pw_link_click(self, **event_args):
        """This method is called when the link is clicked"""
        
        # --------------------------------Tests sur mail
        # mail vide ?
        if self.email_box.text == "":
            AlertHTML.info("Oublie :", "Entrez votre mail !")
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
            AlertHTML.error("Adresse Mail :", "Mail erroné !")
            self.email_box.focus()
            return

        if anvil.server.call('_send_password_reset', self.email_box.text):
            AlertHTML.info("Réinitialisation du Mot de Passe :", f"Un mail de réinitilisation vous a été envoyé à {self.email_box.text}.\n (Lien valide 30 minutes.)")
            open_form('Main',99)     #je retourne et efface l'url

    def email_box_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_validation_click()

    def password_box_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_validation_click()




