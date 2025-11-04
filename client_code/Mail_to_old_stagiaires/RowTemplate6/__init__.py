from ._anvil_designer import RowTemplate6Template
from anvil import *
import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate6(RowTemplate6Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
         # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label_mail.text = self.item['mail']
        try:
            nom_p = self.item['nom'] + " " + self.item['prenom']   # cas où nom prenom vides
        except:
            pass
        self.label_nom.text = nom_p
        self.check_box_envoi.checked = self.item['envoi']
        if self.item['envoi'] is True:
            self.column_panel_1.background = "theme:Vert Foncé"
        try:
            self.label_date_heure.text = str(self.item['Date_time_envoi'])[0:16]  # cas où date encore vide
        except:
            pass
        if self.item['Date_time_envoi'] is None:
            self.label_date_heure.text = ""
        
        self.check_box_selection.checked = self.item['select']
        if self.check_box_selection.checked is True:
            self.check_box_selection.background = "theme:Tertiary"
        else:
            self.check_box_selection.background = "theme:On Primary Container"
            
        self.label_type.text = self.item['type_mail']


    def check_box_envoi_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # Récup de l'id pour MAJ de l'item
        result = anvil.server.call("maj_histo_envoi",self.item,self.check_box_envoi.checked)
        if result is not True:
            alert("Erreur de MAJ")
        if self.item['envoi'] is True:
            self.column_panel_1.background = "theme:Vert Foncé"
        else:
            self.column_panel_1.background = "theme:Primary"
            

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous enlever cet historique ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :     
            result = anvil.server.call("del_histo",self.item)
            if result is not True:
                alert("Item non retiré")
        open_form('Mail_to_old_stagiaires')

    def check_box_selection_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # récupération de la forme mère par  self.f = get_open_form() en init
        self.f = get_open_form()   # récupération de la forme mère pour accéder aux fonctions et composents
        nb = int(self.f.label_nb_select.text)
        print("form mère atteingnable (en modif): ", self.f) 
        
        # Récup de l'id pour MAJ de l'item
        result, nb = anvil.server.call("maj_selection",self.item,self.check_box_selection.checked, nb)
        if result is not True:
            alert("Erreur de MAJ")
        if self.check_box_selection.checked is True:  
            self.check_box_selection.background = "theme:Tertiary"
        else:
            self.check_box_selection.background = "theme:On Primary Container"
        self.f.label_nb_select.text = nb   

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        # test existence dans l'application
        if not app_tables.users.get(email=self.item['mail']):
            # confirmation
            try:
                question = self.item['nom'] + " " + self.item['prenom']   # cas où nom prenom vides
            except:
                question = self.item['nom']
                
            question = f"Voulez-vous vraiment ajouter {question} dans l'application"
            r=alert(question,dismissible=False,buttons=[("oui",True),("non",False)])
            if r :   # oui
                from ...User_add_sans_procedures import User_add_sans_procedures
                open_form('User_add_sans_procedures',self.item['nom'], self.item['prenom'], self.item['tel'], self.item['mail'])
        else:
            alert("Cette personne est déjà enregistrée dans cette application !")  # user existant
            from ...Recherche_stagiaire_v3 import Recherche_stagiaire_v3
            open_form("Recherche_stagiaire_v3")