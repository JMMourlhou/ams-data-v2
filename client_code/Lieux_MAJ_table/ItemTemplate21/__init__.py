from ._anvil_designer import ItemTemplate21Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...AlertHTML import AlertHTML
from ...AlertConfirmHTML import AlertConfirmHTML

class ItemTemplate21(ItemTemplate21Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # Any code you write here will run before the form opens.
        self.text_box_2.text = self.item['lieu']
        self.text_box_1.text = self.item['adresse']
        self.sov_old_adresse = self.item['adresse']
        self.sov_old_lieu = self.item['lieu']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        #r=alert("Voulez-vous vraiment effacer ce lieu ?",dismissible=False,buttons=[("oui",True),("non",False)])
        r = AlertConfirmHTML.ask(
            "Annulation d'un lieu :",
            "<p>Voulez-vous annuler ce lieu ?</p>",
            style="error",
            large = True
        )
        if r :   # oui
            result,nb,liste = anvil.server.call("del_lieu", self.item, self.item['lieu'])
            if result is not True:
                detail=[]
                for stage in liste:
                    detail.append(stage['numero'])
                AlertHTML.error("Erreur :", f"Effacement non effectué, ce lieu est utilisé dans {nb} stage(s) :\nStage(s): {detail}")
                #alert(f"Effacement non effectué, ce lieu est utilisé dans {nb} stage(s) :\nStage(s): {detail}")
                return
            AlertHTML.success("Succès", "Annulation effectuée !")
        open_form("Lieux_MAJ_table")

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r = AlertConfirmHTML.ask(
            "Modification d'un lieu :",
            "<p>Voulez-vous modifier ce lieu ?</p>",
            style="error",
            large = False
        )
        if r :   # oui
            # 1 modif ds les lieux stages 
            result = anvil.server.call("modif_lieu", self.item, self.text_box_1.text, self.text_box_2.text, self.sov_old_lieu)
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert("Modification effectuée !")
            
        else:   # non
            self.text_box_1.text = self.sov_old_adresse
            self.text_box_2.text = self.sov_old_lieu
        self.button_modif.visible = False