from ._anvil_designer import Diplomes_nbTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML


class Diplomes_nb(Diplomes_nbTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        # search de tous les stages existants et affichage
        liste = app_tables.stages.search(
            tables.order_by("num_pv", ascending=True),
            #nb_stagiaires_diplomes=q.not_(0),
            q.not_(q.any_of(
                nb_stagiaires_diplomes=0,
                nb_stagiaires_diplomes=None
            ))
        )
        self.repeating_panel_1.items = liste

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 

    def button_pdf_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass


