from ._anvil_designer import ItemTemplate22Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate22(ItemTemplate22Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.text = self.item['code']
        self.text_box_2.text = self.item['text']
        self.check_box_1.checked = self.item['obligation']
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment effacer ce code ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result = anvil.server.call("del_text_formulaire", self.item)
            if result is not True:
                alert("Erreur: Effacement non effectué !")
                return
            alert("Effacement effectué !")
        open_form("Text_formulaires_MAJ_table")

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment modifier ce code ?",buttons=[("oui",True),("non",False)])
        sov_old_text = self.item['text']
        sov_old_code = self.item['code']
        sov_old_obligation = self.item['obligation']
        if r :   # oui
            # 1 modif text_formulaire
            result = anvil.server.call("modif_text_formulaire", self.item, self.text_box_1.text, self.text_box_2.text, self.check_box_1.checked)
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert("Modification effectuée !")
            
        else:   # non
            self.text_box_1.text = sov_old_code
            self.text_box_2.text = sov_old_text
            self.radio_button_1 = sov_old_obligation
        self.button_modif.visible = False

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_2_change(self, **event_args): # Le code change
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def check_box_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif.visible = True

    