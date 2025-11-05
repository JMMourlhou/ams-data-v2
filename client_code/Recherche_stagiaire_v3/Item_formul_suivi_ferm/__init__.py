from ._anvil_designer import Item_formul_suivi_fermTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Item_formul_suivi_ferm(Item_formul_suivi_fermTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        score = self.item[2]
        if score == 0:
            self.column_panel_1.background = "theme:Error"
        elif score == 1:
            self.column_panel_1.background = "theme:Orange"    
        elif score == 2:
            self.column_panel_1.background = "theme:Jaune Orange"
        elif score == 3:
            self.column_panel_1.background = "theme:Vert Tres Clair"
        elif score == 4:
            self.column_panel_1.background = "theme:Vert Clair"    
        elif score == 5:
            self.column_panel_1.background = "theme:Green"

        self.label_question.text=f"{self.item[0]} - {self.item[1]}"
        self.label_reponse.text=self.item[2]