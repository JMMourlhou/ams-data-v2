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
        liste0 = app_tables.stages.search(
            tables.order_by("num_pv", ascending=True),
            nb_stagiaires_diplomes=q.not_(0),
        )
        liste1=[]
        for stage in liste0:
            if stage['nb_stagiaires_diplomes'] is not None and stage['date_debut'] < date:
                liste1.append(stage)
            
        self.repeating_panel_1.items = liste1

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 

    def button_pdf_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass


