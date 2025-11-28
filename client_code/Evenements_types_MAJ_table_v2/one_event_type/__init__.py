from ._anvil_designer import one_event_typeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class one_event_type(one_event_typeTemplate):
    def __init__(self, item, **properties):
        # Set Form properties and Data Bindings.
        # Any code you write here will run before the form opens.
        self.item = item
        self.button_code.text = self.item['code']
        self.button_type_evnt.text = self.item['type']
        self.button_msg_0.text = self.item['msg_0']
        self.button_msg_1.text = self.item['msg_1']
        self.nb = self.item['code']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.row_to_be_deleted = self.item  # self.check_box_state   Propriété de la forme créée
        
        # j'empêche d'effacer les codes 0 à 3
        if self.nb < 4:
            alert("Ce type d'évenement ne peut être effacé !")
            return

        test = app_tables.events.search(event_typ=self.item)
        if len(test)>0:
            alert(f"Attention, il y a déja {len(test)} évenement(s) enregistré(s)  pour cette catégorie !\n\nEffacez les d'abord avant de détruire cette catégorie d'évenements !")
            return

        r=alert("Voulez-vous vraiment effacer ce type d'évenement ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result = anvil.server.call("del_type_evnt", self.item)
            if result is not True:
                alert("Erreur: Effacement non effectué !")
                return
            alert("Effacement effectué !")
        self.remove_from_parent()

    def button_code_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.row_to_be_modified = self.item  # self.check_box_state   Propriété de la forme créée
        self.raise_event("x-modif")

  

    