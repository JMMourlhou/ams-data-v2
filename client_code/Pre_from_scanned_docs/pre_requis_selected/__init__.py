from ._anvil_designer import pre_requis_selectedTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class pre_requis_selected(pre_requis_selectedTemplate):
    def __init__(self, row_pr, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.row_pr = row_pr
        self.label_pr.text = self.row_pr['requis']

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.pr_row_to_be_deleted = self.row_pr  # self.check_box_state   Propriété de la forme créée
        self.raise_event("x-del")
        self.remove_from_parent()