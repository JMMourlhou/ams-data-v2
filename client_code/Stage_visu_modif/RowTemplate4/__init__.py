from ._anvil_designer import RowTemplate4Template
from anvil import *

import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate4(RowTemplate4Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        
        self.text_box_3.text = self.item['name'].capitalize()+" "+ self.item['user_email']["prenom"].capitalize()
        self.text_box_1.text = self.item['user_email']['email']
        self.text_box_2.text = self.item['user_email']['tel']
        self.check_box_form_satis.checked = self.item['enquete_satisf']
        self.check_box_form_suivi.checked = self.item['enquete_suivi']
        self.init_drop_down_mode_fi()  
   
    def text_box_3_focus(self, **event_args):
        """This method is called when the text area gets focus"""
        mel = self.item['user_email']['email']  
        num_stage = self.item["stage"]['numero']
        from ...Saisie_info_apres_visu import Saisie_info_apres_visu
        open_form('Saisie_info_apres_visu', mel, num_stage, intitule="")

    def text_box_1_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_3_focus()

    def text_box_2_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_3_focus()


    def bt_delete(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Enlever ce stagiaire de ce stage ?",dismissible=False,buttons=[("Non",False),("Oui",True)])
        if r :   #oui   
            stagiaire_row = self.item['user_email']
            stage_num = self.item['numero']
            txt_msg = anvil.server.call("del_stagiaire", stagiaire_row, stage_num)   # module serveur "add_stagiaire"
            alert(txt_msg)
            # réaffichage par initialisation de la forme mère 
            open_form('Stage_visu_modif', self.item['numero']) # réinitialisation de la fenêtre

    def check_box_form_satis_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # Sauvegarde du check box au cas ou l'utilisateur répond 'non'
        sov = self.check_box_form_satis.checked
        
        if self.check_box_form_satis.checked is False:
            r=alert("ATTENTION ! Le formulaire de satisfaction du stagiaire va être annulé.\n\nConfirmez svp ! ",dismissible=False,buttons=[("Non",False),("Oui",True)])
            if not r :   #non
                if sov is False: # je remets à True
                    self.check_box_form_satis.checked = True
                else:
                    self.check_box_form_satis.checked = False
                return
        stagiaire_row=self.item    # formulaire de satisf rempli T/F
        valid = anvil.server.call("init_formulaire_satis_stagiaire", stagiaire_row, self.check_box_form_satis.checked)   # module serveur "add_stagiaire"
        if valid is True:
            alert("Le formulaire a bien été effacé !\n\n Il peut être ré-entré par le stagiaire si nécessaire.")
   
    def check_box_form_suivi_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # Sauvegarde du check box au cas ou l'utilisateur répond 'non'
        sov = self.check_box_form_suivi.checked
        
        if self.check_box_form_suivi.checked is False:
            r=alert("ATTENTION ! Le formulaire de suivi du stagiaire va être annulé.\nIl devra le refaire.\n\nConfirmez svp ! ",dismissible=False,buttons=[("Non",False),("Oui",True)])
            if not r :   #non
                if sov is False: # je remets à True
                    self.check_box_form_suivi.checked = True
                else:
                    self.check_box_form_suivi.checked = False
                return
        stagiaire_row=self.item   # formulaire de suivi rempli T/F
        valid = anvil.server.call("init_formulaire_suivi_stagiaire", stagiaire_row, self.check_box_form_suivi.checked)   # module serveur "add_stagiaire"
        if valid is True:
            alert("Le formulaire a bien été effacé !\n\n Il peut être ré-entré par le stagiaire si nécessaire.")
        
    def init_drop_down_mode_fi(self):
        self.f = get_open_form()   # récupération de la forme mère (Stage_visu_modif) ou (Recherche_stagiaire) pour revenir ds la forme appelante
        liste =[]
        for x in self.f.drop_down_mode_fi.items:
            liste.append((x[0],x[1])) 
        self.drop_down_mode_fi.items = liste
        self.drop_down_mode_fi.selected_value = self.item["financement"]

    def drop_down_mode_fi_change(self, **event_args):
        """This method is called when an item is selected"""
        # sauvegarde du mode de fi si ok 
        nom_p = self.item["name"].capitalize() + " " + self.item["prenom"].capitalize()
        r = alert(
            f"Voulez-vous vraiment Changer le mode de financement pour {nom_p} ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            stagiaire_row=self.item   # Changement du mode de fi
            result = anvil.server.call("modif_mode_fi_1_stagiaire", stagiaire_row, self.drop_down_mode_fi.selected_value)
            if result:
                alert("Modification du mode de financemnt effectuée !")
            else:
                alert("Modification du mode de financemnt NON effectuée !")
        else:
            self.drop_down_mode_fi.selected_value = self.item["financement"]
        
