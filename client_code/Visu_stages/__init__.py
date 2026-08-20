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

        
        # Filtres
        # Drop down codes lieux
        self.drop_down_lieux.items = [(r['lieu'], r) for r in app_tables.lieux.search()]
        # Drop down codes stages
        self.drop_down_code_stage.items = [(r['code'], r) for r in app_tables.codes_stages.search(tables.order_by("code", ascending=True))]
        
        # Initialisation de la liste des stages à afficher
        self.drop_down_mode_fi.items = [(r['code_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("code_fi", ascending=True))]
        
        # si le role du user n'est pas 'O' (CREPS ...), je peux afficher tous les stages
        user=anvil.users.get_user()
        if user['role'] != 'O':
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False))   
        else:
            # récupération du centre du user
            centre = user['centre']
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                    lieu=centre
                                                    )
        self.repeating_panel_1.items = liste_stages
            
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
        
    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        # Initialisation de la liste des stages à afficher
        #self.drop_down_mode_fi.items = [(r['code_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("code_fi", ascending=True))]
        
        # Acquisition du filtre sur le type de stage à afficher
        self.type_stage_row = self.drop_down_code_stage.selected_value
        if self.type_stage_row is None:
            return
       
        
    def drop_down_lieux_change(self, **event_args):
        """This method is called when an item is selected"""
        # Acquisition du filtre sur le type de stage à afficher
        self.lieu_row = self.drop_down_lieux.selected_value
        if self.lieu_row is None:
            return
        self.traitement_filtres()

    def traitement_filtres(self):
        alert(f"filtre: stage: {self.type_stage_row['code']} \n Centre: {self.lieu_row}")
        # si le role du user n'est pas 'O' (CREPS ...), je peux afficher tous les stages
        user=anvil.users.get_user()
        centre = user['centre']  # récupération du centre du user

        if user['role'] = 'O': # Organisme de formation (Creps)..)
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                    code=type_stage_row)   
        else: # pas de user centre 'O'
            #AMS ET MUC
            if self.ams and self.muc:  # Je récupère tous les stages
                liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False))

            if self.ams and not self.muc:
                try:
                    centre = app_tables.lieux.get(lieu="AMS Carnon")
                    alert(centre['lieu'])
                except Exception as e:
                    alert(f"Erreur en lecture du lieu 'AMS Carnon': {e}")
                    return
                if self.drop_down_code_stage.selected_value is None: # tous types de stage 
                    liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                            lieu=centre,
                                                           )
                else: 
                    liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                            lieu=centre,
                                                            code=self.drop_down_code_stage.selected_value
                                                           )
  
        self.repeating_panel_1.items = liste_stages

 







