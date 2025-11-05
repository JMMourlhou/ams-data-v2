from ._anvil_designer import Item_formul_fin_ouvTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Item_formul_fin_ouv(Item_formul_fin_ouvTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label_question.text=f"{self.item[0]} - {self.item[1]}"
        self.label_reponse.text=self.item[2]