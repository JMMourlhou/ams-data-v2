from ._anvil_designer import Pre_R_pour_stagiaire_adminTemplate
from anvil import *

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Pre_R_pour_stagiaire_admin(Pre_R_pour_stagiaire_adminTemplate):
    def __init__(self, num_stage, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()
        self.num_stage = num_stage
        # Any code you write here will run before the form opens.
        #lecture du stage  
        row_stage = app_tables.stages.get(numero=num_stage)
        self.label_1.text = "Gestion des pré-Requis, stage " + row_stage['code']['code'] + " du " + str(row_stage['date_debut'].strftime("%d/%m/%Y"))

        # search des stagiaires de ce stage en SERVEUR
        #liste_stagiaires = anvil.server.call('preparation_liste_pour_panels_stagiaires', row_stage)
        liste_stagiaires = app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True),
            q.fetch_only("user_email", "name"),
            stage=row_stage
        )
        self.repeating_panel_1.items = liste_stagiaires

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)