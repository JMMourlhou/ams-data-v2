from ._anvil_designer import student_rowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class student_row(student_rowTemplate):
    def __init__(self, cpt, row_stagiaire_inscrit, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()
        self.label_nom_prenom.text = f"{cpt} - {row_stagiaire_inscrit['user_email']['nom'].upper()} {row_stagiaire_inscrit['user_email']['prenom'].capitalize()}"
        self.check_box_doc_ok.checked = True
        self.label_nom_prenom.tag = "label"
        self.check_box_doc_ok.tag = "check_box"
        
    def check_box_doc_ok_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.check_box_state = self.check_box_doc_ok.checked   # self.check_box_state   Propriété de la forme créée
        self.raise_event('x-change')
