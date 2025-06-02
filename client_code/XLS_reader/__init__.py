from ._anvil_designer import XLS_readerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class XLS_reader(XLS_readerTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens
        
    """
    CE FICHIER CSV DOIT ETRE CHARGE PAR L'ONGLET DATA FILES (il sera ds la table files)
    """
    # si fichier important, il générera l'erreur "anvil.server.TimeoutError: Server code took too long"
    # DONC, UTILISATION DE LA BG TASK avec timer pour tuer la tache à la fin
    
    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        with anvil.server.no_loading_indicator:
            self.task_csv = anvil.server.call('run_bg_task_csv_reader',file)
            self.timer_1.interval=0.5

    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        try:
            if self.task_csv.is_completed():
                self.timer_1.interval=0
                anvil.server.call('task_killer',self.task_csv)
                alert("Fin de tache")
                list = app_tables.stagiaires_histo.search()
                msg = f"Le fichier des anciens stagiaires contient {len(list)} lignes"
                alert(msg)
        except:
            pass


    
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)
        
        
        