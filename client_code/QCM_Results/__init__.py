from ._anvil_designer import QCM_ResultsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from anvil.js import window # to gain access to the window object
global screen_size
screen_size = window.innerWidth

class QCM_Results(QCM_ResultsTemplate):
    def __init__(self, stage_row, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.         # RECHERCHE des stagiaires du stage sélectionné en Visu_stages 
        self.f = get_open_form()
        if stage_row:
            liste_stagiaires = app_tables.stagiaires_inscrits.search(
                                                                    tables.order_by("name", ascending=True),
                                                                    stage = stage_row
                                                                    )
            if liste_stagiaires:      # stagiaires inscrits ds stage
                self.repeating_panel_1.items = liste_stagiaires


    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""       
        open_form(self.f)
