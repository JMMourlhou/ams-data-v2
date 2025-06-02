from ._anvil_designer import z_Utilitaires_JMTemplate
from anvil import *
import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import French_zone # calcul tps traitement


class z_Utilitaires_JM(z_Utilitaires_JMTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    

    def bt_maj_txt_stagiaires_inscrits_click(self, **event_args):
        """This method is called when the button is clicked"""
        result=anvil.server.call("maj_stagiaires_inscrits_txt")
        alert(result)

    def bt_del_qcm_2_mois_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .. import z_loop_on_tables
        result=z_loop_on_tables.del_qcm_results_unsuccessed_old()
        alert(result)

    def bt_del_qcm_essai_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .. import z_loop_on_tables
        result=z_loop_on_tables.del_qcm_results_essai()
        alert(result)


    
    #================================================================================================================
    # EN BG TASK
    # Boucle sur toute la table pre_requis_stagiaire pour maj colonnes nom, prenom, numero, pr en clair txt 
    # et effact de pr si le user n'existe plus
    # ===========================  BG Task  ========================================================
    def bt_maj_txt_pre_requis_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            self.start = French_zone.french_zone_time()  # pour calcul du tps de traitement
            alert("Début du traitement")
            self.task_maj_pr = anvil.server.call('run_bg_task_maj_pr_stagiaires_txt')
            self.timer_1.interval=0.5
            
    def timer_1_tick(self, **event_args):
        """This method is called Every 0.5 seconds. Does not trigger if [interval] is 0."""
        if self.task_maj_pr.is_completed():
            self.end = French_zone.french_zone_time()  # pour calcul du tps de traitement
            alert(f"Maj des colonnes txt en {self.end-self.start}")
            self.timer_1.interval=0
            anvil.server.call('task_killer',self.task_maj_pr)

    def bt_csv_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('XLS_reader')
