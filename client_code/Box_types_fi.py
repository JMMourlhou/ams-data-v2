from ._anvil_designer import Box_types_fiTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Box_types_fi(Box_types_fiTemplate):
    def __init__(self, stagiaire_row, stage, **properties):
        # Set Form properties and Data Bindings.
        
        # Any code you write here will run before the form opens.
        self.init_components(**properties)
        self.code_fi = None
        self.stagiaire_row = stagiaire_row
        self.stage = stage
        
        # Initialisation Drop down mode de financemnt
        self.drop_down_fi.items = [(r['intitule_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("intitule_fi", ascending=True))]

    def drop_down_fi_change(self, **event_args):
        """This method is called when an item is selected"""
        row = self.drop_down_fi.selected_value
        self.code_fi = row['code_fi']
        self.button_ok.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.remove_from_parent()
        
    def button_ok_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_annuler.visible = False
  
        txt_msg = anvil.server.call("add_stagiaire", self.stagiaire_row, self.stage,  self.code_fi, "bt_recherche", 0)
        alert(txt_msg)
        open_form('Recherche_stagiaire_v2', self.stage)  # réouvre la forme mère pour mettre à jour l'affichage de l'histo

        