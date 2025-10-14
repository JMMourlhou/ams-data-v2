from ._anvil_designer import ItemTemplate17Template
from anvil import *
import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Stage_suivi_rep_ouvertes import (Stage_suivi_rep_ouvertes)   #  Forme ajoutée pour questions ouvertes
from ..vide import vide
from ...PageBreak import PageBreak
# AFFICHAGE DU PRENOM / NOM du stagiaire ou Tuteur
# Recherche et affichage de ses Q/Rep ouvertes et fermées

class ItemTemplate17(ItemTemplate17Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.

        # lecture fichier temp (get_open_form ne fonctionne pas si je suis en BGT, génération du pdf de suivi)
        temp_row = app_tables.temp.search()[0]  # lecture de 1ere ligne fichier temp
        type_suivi = temp_row['type_suivi']

        # erreur si tel pas rentré
        try:
            self.label_1.text = self.item['prenom'] +" "+ self.item['name']+" "+ self.item['user_email']['tel']
        except:
            self.label_1.text = self.item['prenom'] +" "+ self.item['name']
            
        # recherche du ou des formulaires du stagiaire ou Tuteur 
        if type_suivi == "S":
            list = app_tables.stage_suivi.search(
                                                user_email=self.item['user_email']['email'],
                                                stage_num_txt=str(self.item['numero']),
                                                user_role = "S"
                                                )
            
            
        if type_suivi == "T":
                       
            list = app_tables.stage_suivi.search(
                                                user_email=self.item['user_email']['email'],
                                                stage_num_txt=str(self.item['pour_stage_num']['numero']),    # 
                                                user_role = "T"
                                                )
        nb_formulaires = len(list)
        
        #Boucle sur les formulaires
        rep_ouv = {}
        qt=0
        cpt = 0
        val = []
        for formulaire in list:
            #Boucle sur 1 formulaire 
            cpt += 1
            # Affichage des réponses ouvertes
            rep_ouv = formulaire['rep_dico_rep_ouv']
            print(rep_ouv)
            for cle_num_question, val in rep_ouv.items():
                #Boucle sur chaque rep ouverte
                qt = cle_num_question
                liste_rep = val
                self.column_panel_content.add_component(Stage_suivi_rep_ouvertes(qt, liste_rep, True, "ouvertes"))   # True; je mets q° et rep sur 2 lignes

            # Affichage des réponses fermées
            rep_ferm = formulaire['rep_dico_rep_ferm']
            #print(rep_ferm)
            for cle_num_question, val in rep_ferm.items():
                #Boucle sur chaque rep ouverte
                qt = cle_num_question
                liste_rep = val
                self.column_panel_content.add_component(Stage_suivi_rep_ouvertes(qt, liste_rep, True, "fermées"))   # True; je mets q° et rep sur 1 ligne

            if cpt < nb_formulaires:
                titre = self.item['user_email']['nom'] + " " + self.item['user_email']['prenom'] 
                self.column_panel_content.add_component(vide(titre))
                                                        
    def form_show(self, **event_args):
        self.add_component(PageBreak()) 