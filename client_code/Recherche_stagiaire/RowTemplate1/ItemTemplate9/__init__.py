from ._anvil_designer import ItemTemplate9Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate9(ItemTemplate9Template):                             # bt Historique a été cliqué
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        if self.item['user_email']['role']=="S": 
            self.button_detail_histo.text = self.item['stage']['code']['code'] +" du " + str(self.item['stage']['date_debut'])
        else:
            self.button_detail_histo.text = self.item['stage']['code']['code']

    def button_detail_histo_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Stage_visu_modif import Stage_visu_modif
        id=self.item['stage'].get_id()
        open_form('Stage_visu_modif', int(self.item['numero']), id, False)  # False: ne pas effectuer les BG tasks
