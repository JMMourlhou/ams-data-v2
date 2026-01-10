from ._anvil_designer import ItemTemplate9Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate9(ItemTemplate9Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_pv.text = self.item['num_pv']
        self.text_box_num.text = self.item['numero']
        self.text_box_date.text = self.item['date_debut']
        self.text_box_nom.text = self.item['code_txt']
        self.text_box_nb_diplomes.text = self.item['nb_stagiaires_diplomes']
        
        