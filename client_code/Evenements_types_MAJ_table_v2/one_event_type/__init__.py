from ._anvil_designer import one_event_typeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class one_event_type(one_event_typeTemplate):
    def __init__(self, item, **properties):
        # Set Form properties and Data Bindings.
        # Any code you write here will run before the form opens.
        self.item = item
        self.text_box_1.text = self.item['type']
        self.text_box_2.text = self.item['code']
        self.text_box_3.text = self.item['msg_0']
        self.text_box_4.text = self.item['msg_1']
        self.check_box_1.checked = item['mot_clef_setup']


    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.row_to_be_deleted = self.item  # self.check_box_state   Propriété de la forme créée
        self.raise_event("x-del")     

    def text_box_2_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.row_to_be_modified = self.item  # self.check_box_state   Propriété de la forme créée
        self.raise_event("x-modif")