from ._anvil_designer import ItemTemplate9Template
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate9(ItemTemplate9Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.button_num_stage.text = self.item['stage_num_txt']
        self.button_type_stage.text = self.item['stage_type_txt']
        
