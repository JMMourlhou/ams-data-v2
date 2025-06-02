from ._anvil_designer import ItemTemplate26Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate26(ItemTemplate26Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_2.text = self.item['intitulé']
        self.text_box_1.text = self.item['code']
        self.text_box_3.text = self.item['type_stage']
        
        self.sov_old_code = self.item['code']
        self.sov_old_intitul = self.item['intitulé']
        self.sov_old_type_st = self.item['type_stage']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        # vérif si des stages existent
        list=app_tables.stages.search(code=self.item)
        nb = len(list)
        if nb > 0:
            detail=[]
            for stage in list:
                detail.append(stage['numero'])
            alert(f"Effacement non effectué, ce type de stage est utilisé dans {nb} stage(s) :\nStage(s): {detail}")
            return
        
        r=alert("Voulez-vous vraiment effacer ce type de stage ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result = anvil.server.call("del_type_stage", self.item)
            if result is not True:
                alert("Effacement de ce type de stage non effectué !")
        open_form("Stage_MAJ_Table")

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment modifier ce type de stage ?",buttons=[("oui",True),("non",False)])
        if r :   # oui
            # 1 modif ds les stages 
            result = anvil.server.call("modif_type_stage", self.item, self.text_box_1.text, self.text_box_2.text, self.text_box_3.text, self.sov_old_intitul)
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert("Modification effectuée !")
            
        else:   # non
            self.text_box_1.text = self.sov_old_code
            self.text_box_2.text = self.sov_old_intitul
            self.text_box_3.text = self.sov_old_type_st
            
        self.button_modif.visible = False
