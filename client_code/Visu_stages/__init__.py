from ._anvil_designer import Visu_stagesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Stage_visu_modif

from anvil.js import window # to gain access to the window object (taille fenêtre)
global screen_size
screen_size = window.innerWidth

class Visu_stages(Visu_stagesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.    
        if screen_size < 800:
            #self.label_en_tete.text = "Stage du ...              Type           Inscription"
            pass
        
        # Initilisation de la liste des stages à afficher
        
        # drop_down mode fi pour le repeat_panel de Stage_visu_modif
        self.drop_down_mode_fi.items = [(r['code_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("code_fi", ascending=True))]
        
        liste_stages = app_tables.stages.search(q.fetch_only("numero", "type_stage"),
                                                                tables.order_by("date_debut", ascending=False)
                                                               )   
        self.repeating_panel_1.items = liste_stages
        self.repeating_panel_1.visible = True
            
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)


    def creation_stage_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_creation import Stage_creation
        open_form('Stage_creation')

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.column_panel_header.scroll_into_view()








