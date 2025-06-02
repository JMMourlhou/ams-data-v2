from ._anvil_designer import ItemTemplate13Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate13(ItemTemplate13Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_2.text = self.item['code_pre_requis']
        self.text_box_1.text = self.item['requis']
        self.text_box_3.text = self.item['commentaires']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment effacer ce pré-requis pour tous les stages et stagiaires ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result,nb = anvil.server.call("del_pr", self.item, self.item['code_pre_requis'])
            if result is not True:
                alert("ERREUR, Effacement non effectué !")
                return
            alert(f"Effacement effectué pour {nb} pré-requis Stagiaires!")
        open_form("Pre_R_MAJ_table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_2_change(self, **event_args): # Le code change
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_modif.visible = True


    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment modifier ce Pré-requis ?",buttons=[("oui",True),("non",False)])
        sov_old_pr = self.item['requis']
        sov_old_code = self.item['code_pre_requis']
        if r :   # oui
            # 1 modif ds les pre-requis stagiaires 
            result, nb = anvil.server.call("modif_pr", self.item, self.text_box_1.text, self.text_box_2.text,  self.text_box_3.text, sov_old_code)
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert(f"Modification effectuée sur {nb} pré-requis des Stagiaires!")
            
        else:   # non
            self.text_box_1.text = sov_old_pr
            self.text_box_2.text = sov_old_code
        self.button_modif.visible = False

   

    
            