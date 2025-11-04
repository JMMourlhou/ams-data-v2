from ._anvil_designer import RowTemplate7Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate7(RowTemplate7Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.sov_raison_modif = ""
        
        # Any code you write here will run before the form opens.
        self.button_role.text = self.item['role']
        self.button_nom.text = self.item['nom']
        self.button_prenom.text = self.item['prenom']
        self.button_email.text = self.item['email']
        
        self.text_box_nb_pw_failures.text = self.item['n_password_failures']
        self.check_box_conf_mail.checked = self.item['confirmed_email']
        self.check_box_cpt_enabled.checked = self.item['enabled']
        self.sov_old_conf_mail = self.item['confirmed_email']
        self.sov_old_enabled = self.item['enabled']
        self.sov_old_pw = self.item['n_password_failures']
        
        self.button_sign_up.text = self.item['signed_up']
        self.button_last_login.text = self.item['last_login']

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment modifier cette ligne ?",buttons=[("oui",True),("non",False)])
        if r :   # oui
            try:
                nb = int(self.text_box_nb_pw_failures.text)     # si self.text_box_nb_pw_failures.text est null
            except:
                nb = 0
                
            result=anvil.server.call('modify_users_from_parameters',
                                     self.item,
                                     self.check_box_conf_mail.checked,
                                     self.check_box_cpt_enabled.checked,
                                     nb
                                    )
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            open_form('Users_search', self.sov_raison_modif)
        else:   # non
            self.check_box_conf_mail.checked = self.sov_old_conf_mail
            self.check_box_cpt_enabled.checked = self.sov_old_enabled
            self.text_box_nb_pw_failures.text = self.sov_old_pw
            self.button_modif.visible = False
        self.button_modif.visible = False

    def check_box_conf_mail_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.sov_raison_modif = "confirmation"
        self.button_modif.visible = True

    def check_box_cpt_enabled_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.sov_raison_modif = "enabled"
        self.button_modif.visible = True

    def button_role_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ...Recherche_stagiaire_v3 import Recherche_stagiaire_v3
        open_form('Recherche_stagiaire_v3', self.item)

    def text_box_nb_pw_failures_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        
        self.button_modif.visible = True




  

    
        
        
        