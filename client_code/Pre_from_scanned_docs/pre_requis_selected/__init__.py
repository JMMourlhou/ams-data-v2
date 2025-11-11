from ._anvil_designer import pre_requis_selectedTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class pre_requis_selected(pre_requis_selectedTemplate):
    def __init__(self, cpt, row_stagiaire_inscrit, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        row=app_tables.pre_requis.get(code_pre_requis=self.item)
        try:
            self.label_pr.text = row['requis']
        except Exception as e:
            alert(f"Erreur: Un code pré-requis n'existe plus en table pre_requis: {e}")
   

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.pr_code_to_be_deleted = self.item['code_pre_requis']  # self.check_box_state   Propriété de la forme créée
        self.raise_event("x-del")
