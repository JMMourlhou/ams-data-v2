from ._anvil_designer import Item_formulaires_suivis_listeTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Item_formulaires_suivis_liste(Item_formulaires_suivis_listeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()  # form appelante
        # Any code you write here will run before the form opens.
        self.button_num_stage.text = f"Num {self.item['stage_num_txt']}"
        self.button_type_stage.text = f"Suivi de stage {self.item['stage_type_txt']}"
        self.button_date_heure.text = f"Saisi le {self.item['date_heure'][0:16]}"

    def button_type_stage_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.f.repeating_panel_formul_suivi_questions_ouvertes.visible is False:
            # génération de la liste à afficher
            # QUESIONS OUVERTES
            liste_questions_ouv=[]
            # dico questions ouvertes
            dico_rep_ouv = self.item["rep_dico_rep_ouv"]  # dico questions ouvertes du formulaire
            # Boucle sur le dictionaire ouvert du formulaire
            for cle, val in dico_rep_ouv.items():
                num_question = cle
                question = val[0]
                reponse = val[1]
                liste_questions_ouv.append((num_question,question,reponse))
            if len(liste_questions_ouv) > 0:    
                self.f.repeating_panel_formul_suivi_questions_ouvertes.visible = True
                self.f.repeating_panel_formul_suivi_questions_ouvertes.items = liste_questions_ouv
        else:
            self.f.repeating_panel_formul_suivi_questions_ouvertes.visible = False
        """
        # QUESIONS FERMEES
        if self.f.repeating_panel_formul_fin_questions_fermees.visible is False:
            liste_questions_ferm=[]
            # dico questions ouvertes
            dico_rep_ferm = self.item["rep_dico_rep_ferm"]  # dico questions ouvertes du formulaire
            # Boucle sur le dictionaire ouvert du formulaire
            for cle, val in dico_rep_ferm.items():
                num_question = cle
                question = val[0]
                reponse = val[1]
                liste_questions_ferm.append((num_question,question,reponse))
            if len(liste_questions_ferm) > 0:    
                self.f.repeating_panel_formul_fin_questions_fermees.visible = True
                self.f.repeating_panel_formul_fin_questions_fermees.items = liste_questions_ferm
            self.button_download.visible = True
        else:
            self.f.repeating_panel_formul_fin_questions_fermees.visible = False
        """