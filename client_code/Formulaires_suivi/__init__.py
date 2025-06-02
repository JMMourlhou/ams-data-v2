from ._anvil_designer import Formulaires_suiviTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Formulaires_suivi(Formulaires_suiviTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        list = app_tables.stage_suivi.search(tables.order_by("stage_num_txt", ascending=False))
        self.repeating_panel_1.items = list
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")
