from ._anvil_designer import pr_selected_listTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class pr_selected_list(pr_selected_listTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        row=app_tables.pre_requis.get(code_pre_requis=self.item)
        try:
            self.text_box_1.text = "  " + row['requis']
            self.button_annuler.tag = row['code_pre_requis']
        except:
            alert("Un code pré-requis n'existe plus en table pre_requis")