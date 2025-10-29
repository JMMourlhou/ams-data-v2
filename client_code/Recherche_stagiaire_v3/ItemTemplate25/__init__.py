from ._anvil_designer import ItemTemplate25Template
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate25(ItemTemplate25Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        if self.item['prenom'] is not None:    # si prénom None, erreur
            self.button_1.text = self.item['nom']+" "+self.item['prenom']
            self.button_role.text = self.item['role']
        else:
            self.button_1.text = self.item['nom']

        self.button_3.text = self.item['email']
        self.button_4.text = self.item['tel']

    def button_role_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    
        
