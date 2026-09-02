from ._anvil_designer import ItemTemplate25_histoTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate25_histo(ItemTemplate25_histoTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        
        # Par défaut
        self.button_detail_histo.text = self.item['stage']['code']['code'] 
        
        if self.item['user_email']['role'] == "S": 
            self.button_detail_histo.text =  f"{self.item['stage']['code']['code']} du {str(self.item['stage']['date_debut'])} / #{self.item['stage']['numero']} "
            
        if self.item['user_email']['role'] in ("F", "T", "B", "A", "J", "V"):
            self.button_detail_histo.text = f"{self.item['stage']['code']['code']} / #{self.item['stage']['numero']} "

    def button_detail_histo_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ...Stage_visu_modif import Stage_visu_modif
        id=self.item['stage'].get_id()
        open_form('Stage_visu_modif', int(self.item['numero']), id, False)  # False: ne pas effectuer les BG tasks