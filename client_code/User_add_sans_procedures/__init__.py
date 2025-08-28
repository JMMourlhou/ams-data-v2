from ._anvil_designer import User_add_sans_proceduresTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
from .. import Mail_valideur  # pour button_export_xls_click
from .. import French_zone # POur acquisition de date et heure Francaise (Browser time)

class User_add_sans_procedures(User_add_sans_proceduresTemplate):
    def __init__(self, nom="", prenom="", tel="", mail="" ,**properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        #self.text_box_role.text = "T"
        self.text_box_nom.text = nom
        self.text_box_prenom.text = prenom
        self.text_box_tel.text = tel
        self.text_box_mail.text = mail
        if nom != "":
            self.button_valid.visible = True
        # Any code you write here will run before the form opens.
        
    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_add.visible = True

    def text_box_nom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        if len(self.text_box_mail.text) > 8:
            self.button_valid.visible = True

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        if len(self.text_box_nom.text) < 3:
            alert("Le nom n'est pas assez long !")
            self.text_box_nom.focus()
            return
        """
        if len(self.text_box_prenom.text) < 3:
            alert("Le prénom n'est pas assez long !")
            self.text_box_prenom.focus()
            return
        """
        test_role = ["S","s","F","f","T","t","B","b","A","a","V","v"] # je n'accepte que ces lettres, minuscules accptées car upper ensuite
        if self.text_box_role.text not in test_role:
            alert("Le role doit être soit: S, F, T, B, A, V !")
            self.text_box_role.focus()
            return
        # Mail format validation
        self.mail = self.text_box_mail.text.lower()
        result = Mail_valideur.is_valid_email(self.mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            alert("Le mail n'a pas le bon format !")
            self.text_box_mail.focus()
            return

        result = anvil.server.call("new_user",
                                   self.text_box_nom.text.capitalize(),
                                   self.text_box_prenom.text.capitalize(),
                                   self.text_box_tel.text,
                                   self.text_box_mail.text,
                                   self.text_box_role.text.upper(),
                                   signed_up = French_zone.french_zone_time(),  # importé en ht de ce script
                                  )
        if result is not None:
            alert(result)  # user existant
            from ..Recherche_stagiaire import Recherche_stagiaire
            open_form("Recherche_stagiaire")
        else:
            alert("Création effectuée !")
        open_form('User_add_sans_procedures')

    
