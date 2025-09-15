from ._anvil_designer import Stage_suivi_rep_ouvertesTemplate
from anvil import *

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
#from anvil_extras.PageBreak import PageBreak


# AFFICHAGE DES RESULTATS pour le formulaire de suivi
# APPELE PAR LA FORM 'S.ItemTemplate17' par add component:


class Stage_suivi_rep_ouvertes(Stage_suivi_rep_ouvertesTemplate):
    def __init__(self, qt, list_rep="", concatenate = False, type="ouvertes", **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.type = type
        
        #self.label_question.text = qt
        if concatenate is False:       # Question ouvertes: J'affiche la question sur une ligne et la rep sur la suivante
            for rep in list_rep:
                self.tb = RichText(
                    content=rep,
                    align="left",
                    spacing_above="none",
                    background="",
                    foreground="White",
                    # bold=False,
                    font_size=14,
                    # enabled = False
                    spacing_below="none",
                )
                self.column_panel_reponses.add_component(self.tb)  # add 1 des réponses)   
            
        if concatenate is True:
            text = ""
            cpt = 0
            for ligne in list_rep:
                cpt += 1
                text = text +"  "+ str(ligne) 
                if cpt == 2:            # après avoir lu la rep je peux afficher
                    
                    self.tb = RichText(
                                        content=text,
                                        align=self.alignement(),
                                        spacing_above="none",
                                        background=self.couleur_background(ligne),
                                        foreground=self.couleur_foreground(ligne),
                                        #bold=True,
                                        font_size=14,
                                        # enabled = False
                                        spacing_below="none",
                                     )
                    self.column_panel_reponses.add_component(self.tb)  # add 1 des réponses)
                    
    def couleur_background(self, ligne, **event_args):  
        if self.type != "ouvertes":   # rep fermées, j'affiche les couleurs correspondant aux réponses
            bg_couleur = ""
            if ligne == 0:
                bg_couleur = "theme:Error"
            if ligne == 1:
                bg_couleur = "theme:Orange"    
            if ligne == 2:
                bg_couleur = "theme:Jaune Orange"
            if ligne == 3:
                bg_couleur = "theme:Vert Tres Clair"
            if ligne == 4:
                bg_couleur = "theme:Vert Clair"    
            if ligne == 5:
                bg_couleur = "theme:Green"
        else: # rep fermées
            bg_couleur = "theme:Gray 300"    # gris clair
        return bg_couleur
        
    def couleur_foreground(self, ligne, **event_args):  
        if self.type != "ouvertes":   # rep fermées, j'affiche les couleurs correspondant aux réponses
            fg_couleur = ""
            if ligne == 0:
                fg_couleur = "white"
            if ligne == 1:
                fg_couleur = "white"    
            if ligne == 2:
                fg_couleur = "black"
            if ligne == 3:
                fg_couleur = "black"
            if ligne == 4:
                fg_couleur = "white"    
            if ligne == 5:
                fg_couleur = "white"
        else: # rep fermées
            fg_couleur = "black"    # gris clair
        return fg_couleur
        
    def alignement(self, **event_args):  
        align = "center"
        if self.type == "ouvertes":   # rep ouvertes, j'affiche à gauche
            align = "left"
        return align  

"""
    def form_show(self, **event_args):
        self.add_component(
            PageBreak()
        )  # si en création de pdf, je saute une page ts les 25 images, NE FONCTIONNE PAS !!!
"""