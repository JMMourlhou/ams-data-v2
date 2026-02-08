from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate1(RowTemplate1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        """
        Pas besoin d'initialiser ds l'init
        Aller ds l'entête des colonnes et rentrer num_pv (le nom de la colonne ds la table)
        c'est tout.
        bien sûr, initiliser la liste comme d'habitude:
        self.repeating_panel_1.items = liste1
        """