from ._anvil_designer import ItemTemplate7Template
from anvil import *
import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate7(ItemTemplate7Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run before the form opens.
        self.repeating_panel_qcm_results.visible = False
        self.button_nom_prenom.text = self.item['user_email']['nom']+" "+self.item['user_email']['prenom']
        
        # recherche des qcm de ce user pour le stage sélectionné ds Visu_stages
        qcm_results = app_tables.qcm_result.search(
                                                    tables.order_by("time", ascending=False),
                                                    user_qcm = self.item['user_email']
                                                    )
        if len(qcm_results)>0:      # stagiaires inscrits ds stage
                self.repeating_panel_qcm_results.items = qcm_results
        else:
            self.button_nom_prenom.background = "grey"
            self.button_nom_prenom.foreground = "white"
    
    def button_nom_prenom_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        if self.repeating_panel_qcm_results.visible is True:
            self.repeating_panel_qcm_results.visible = False
        else:
            self.repeating_panel_qcm_results.visible = True
        
    

