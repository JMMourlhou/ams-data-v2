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
        self.lieu_row = None
        self.type_stage_row = None
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
            # Pas d'affichage des filtres pour un autre OF (Creps...)
            self.column_panel_filtres.visible = False
        #Affichage des stages    
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
        # Acquisition du filtre sur le type de stage à afficher
        self.type_stage_row = self.drop_down_code_stage.selected_value
        #if self.type_stage_row is None:
        #    return
        self.traitement_filtres()
        
    def drop_down_lieux_change(self, **event_args):
        # Acquisition du filtre sur le centre de formation
        self.lieu_row = self.drop_down_lieux.selected_value
        #if self.lieu_row is None:
        #    return
        self.traitement_filtres()

    # Traitement des filtres Type et Centre de formation (pas du num de stage)
    def traitement_filtres(self):
        #alert(f"filtre: stage: {self.type_stage_row} \n Centre: {self.lieu_row}")

        # Les 2 drop down ne sont pas sélectionnées: On affiche tout
        if self.type_stage_row is None and self.lieu_row is None:
            self.drop_down_code_stage.foreground = "theme:On Primary"
            self.drop_down_lieux.foreground = "theme:On Primary"
            self.text_box_num_stage.foreground = "theme:On Primary"
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                   )
            self.text_box_num_stage.text = ""

        if self.type_stage_row is not None and self.lieu_row is not None:
            self.drop_down_code_stage.foreground = "red"
            self.drop_down_lieux.foreground = "red"
            self.text_box_num_stage.foreground = "theme:On Primary"
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                    lieu=self.lieu_row,
                                                    code=self.type_stage_row
                                                )
            self.text_box_num_stage.text = ""
            
        if self.type_stage_row is None and self.lieu_row is not None:
            self.drop_down_code_stage.foreground = "theme:On Primary"
            self.drop_down_lieux.foreground = "red"
            self.text_box_num_stage.foreground = "theme:On Primary"
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                    lieu=self.lieu_row,
                                                   )
            self.text_box_num_stage.text = ""
        
        if self.type_stage_row is not None and self.lieu_row is None:
            self.drop_down_code_stage.foreground = "red"
            self.drop_down_lieux.foreground = "theme:On Primary"
            self.text_box_num_stage.foreground = "theme:On Primary"
            liste_stages = app_tables.stages.search(tables.order_by("date_debut", ascending=False),
                                                    code=self.type_stage_row
                                                   )
            self.text_box_num_stage.text = ""
            
        # Affichage
        self.repeating_panel_1.items = liste_stages


    def text_box_num_stage_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.num_stage_txt = self.text_box_num_stage.text
        try: 
            self.drop_down_code_stage.foreground = "theme:On Primary"
            self.drop_down_lieux.foreground = "theme:On Primary"
            self.text_box_num_stage.foreground = "red"
            self.num_stage = int(self.num_stage_txt )
            stage_row = app_tables.stages.get(numero=self.num_stage)
            # Affichage
            self.repeating_panel_1.items = list(stage_row)
        except Exception as e:
            alert(f"Entrez un chiffre, SVP ! \n \n {e}")
            self.text_box_num_stage.text = ""
            self.text_box_num_stage.focus()

    
    def text_box_num_stage_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_num_stage.text = ""

 







