from ._anvil_designer import Box_types_fiTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Box_types_fi(Box_types_fiTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.f = get_open_form()
        # Initialisation Drop down mode de financemnt
        self.drop_down_fi.items = [(r['intitule_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("intitule_fi", ascending=True))]

    def drop_down_fi_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.drop_down_fi.selected_value is None: 
            alert("Vous devez sélectionner un mode de financement !")
            return

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
        