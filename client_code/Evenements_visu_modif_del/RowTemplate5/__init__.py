from ._anvil_designer import RowTemplate5Template
from anvil import *
import anvil.server

import anvil.tables as tables
from anvil.tables import app_tables


class RowTemplate5(RowTemplate5Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        #self.f = get_open_form()   # Récup du nom de la forme mère
        #if self.item['auto_sov'] is True:
        #    self.button_date.foreground = "red"
        self.button_date.text = self.item['date']
        self.button_mot_clef.text = self.item['mot_clef']
        self.button_lieu.text = self.item['lieu_text']
        

    def modif(self, **event_args):
        """This method is called when the button is clicked"""
        id = self.item.get_id()
        row_to_be_modified = app_tables.events.get_by_id(id)
        open_form("Evenements_v2_word_processor", row_to_be_modified, "modif")  # Mode modif 

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        type_evnt = self.item["type_event"]
        r=alert("Voulez-vous vraiment effacer cet évenement ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result = anvil.server.call("del_event", self.item)
            if result is not True:
                alert("ERREUR, Effacement non effectué !")
                return
            alert("Effacement effectué !")
            
        # Récupération du contenu de la drop_down en form appelante
        # renvoyer le type d'évenemnt actuel: creation 
        row = app_tables.event_types.get(type=type_evnt)
        from .. import Evenements_visu_modif_del
        open_form("Evenements_visu_modif_del", row)
