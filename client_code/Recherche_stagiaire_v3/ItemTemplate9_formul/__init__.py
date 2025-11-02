from ._anvil_designer import ItemTemplate9_formulTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate9_formul(ItemTemplate9_formulTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.button_num_stage.text = f"Num {self.item['stage_num_txt']}"
        self.button_type_stage.text = f"Fin de stage {self.item['stage_type_txt']}"
        self.button_date_heure.text = f"Saisi le {self.item['date_heure'][0:16]}"
