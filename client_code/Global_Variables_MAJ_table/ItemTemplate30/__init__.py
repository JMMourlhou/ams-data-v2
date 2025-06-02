from ._anvil_designer import ItemTemplate30Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate30(ItemTemplate30Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # Any code you write here will run before the form opens.
        self.text_box_1.text = self.item['name']
        self.text_box_2.text = self.item['value']
        self.text_box_3.text = self.item['Commentaires']
        
        self.sov_old_name = self.item['name']
        self.sov_old_value = self.item['value']
        self.sov_old_commentaires = self.item['Commentaires']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""

        r=alert("Voulez-vous vraiment effacer cette variable globale ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result = anvil.server.call("del_var_globale", self.item)
            if result is not True:
                alert("Effacement de cette variable globale non effectué !")
        open_form("Global_Variables_MAJ_table")

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment modifier cette variable globale ?",buttons=[("oui",True),("non",False)])
        if r :   # oui
            # 1 modif ds les stages 
            result = anvil.server.call("modif_var_globale", self.item, self.text_box_1.text, self.text_box_2.text, self.text_box_3.text)
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                self.button_modif.visible = False
                return
            alert("Modification effectuée !")
        else:   # non
            self.text_box_1.text = self.sov_old_name
            self.text_box_2.text = self.sov_old_value
            self.text_box_3.text = self.sov_old_commentaires
            
        self.button_modif.visible = False

    