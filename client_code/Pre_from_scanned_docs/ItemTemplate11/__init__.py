from ._anvil_designer import ItemTemplate11Template
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate11(ItemTemplate11Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # Any code you write here will run before the form opens.
        self.label_nom_prenom.text = f"{self.item['user_email']['nom']} {self.item['user_email']['prenom']}"
        self.check_box_doc_ok.checked = True

    def check_box_doc_ok_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_doc_ok.checked is True:
            self.check_box_doc_ok.checked = False
            # decrémentation
            #
        else: # False, reset to True
            self.check_box_doc_ok.checked = True
            # incrémentation
            # 