from ._anvil_designer import Stage_form_com_results_stagiaireTemplate
from .. import French_zone  # POur acquisition de date et heure Francaise (Browser time)
from anvil import *

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# Le stagiaire affiche ses propres résultats en communication
class Stage_form_com_results_stagiaire(Stage_form_com_results_stagiaireTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.user = anvil.users.get_user()
        if self.user:
            # Initialisation de la drop down dates 
            self.liste0 = app_tables.com.search(user=self.user)
            print("nb d'évaluations pour ce stagiaire ; ", len(self.liste0))
            if len(self.liste0) > 0: 
                liste_test = []
                liste1 = []
                for row in self.liste0:
                    if row["date"] not in liste_test:
                        liste_test.append(row["date"])   # date, row_intervention
                        liste1.append((row["date"],row ))   # date, row_intervention
                self.drop_down_date.items = liste1

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form("Main", 99)

    def drop_down_date_change(self, **event_args):
        """This method is called when an item is selected"""
        self.com_row = self.drop_down_date.selected_value
        if self.com_row is None:
            alert("Vous devez sélectionner une date !")
            self.drop_down_date.focus()
            return
        self.label_cadre.visible = True
        cadre = self.com_row["cadre"]
        self.label_cadre.text = f"({cadre})"
        # sélection des formulaires saisis à la date sélectionnée
        liste_formulaires = app_tables.com.search(date=self.com_row["date"],
                                                  user=self.user
                                                 )
        nb_formulaires = len(liste_formulaires)
        max_points_ferm = nb_formulaires * 5      # max de points possibles pour une question
        #  ================================================================  Affichage résultats
        # extraction du stage par lecture du premier formulaire de la liste
        first_row = liste_formulaires[0]
        stage_row = first_row["stage_row"]
        # extraction des 2 dictionnaires du stage
        dico_q_ferm = stage_row["com_ferm"]
        dico_q_ouv = stage_row["com_ouv"]
        # nb_questions_ferm  
        nb_questions_ferm = int(dico_q_ferm["NBQ"])  # nb de questions fermées ds le dico
        #alert(f"nb de questions ferm : {nb_questions_ferm}")
        # nb_questions_ouv
        nb_questions_ouvertes = int(dico_q_ouv["NBQ"])  # nb de questions fermées ds le dico
        #alert(f"nb de question ouv: {nb_questions_ouvertes}")
        
        # =========================== Boucle sur tous les formulaires pour les questions fermées
        # initialisation des compteurs
        points_q1 = 0
        points_q2 = 0
        points_q3 = 0
        points_q4 = 0
        points_q5 = 0
        points_q6 = 0
        points_q7 = 0
        points_q8 = 0
        points_q9 = 0
        points_q10 = 0

        rep_ouv1 = ""
        rep_ouv2 = ""
        rep_ouv3 = ""
        rep_ouv4 = ""
        rep_ouv5 = ""
        rep_ouv6 = ""
        rep_ouv7 = ""
        rep_ouv8 = ""
        rep_ouv9 = ""
        rep_ouv10 = ""
        
        # boucle sur toutes les évaluations de ce stagiaire, pour la date sélectionnée
        for formulaire in liste_formulaires:
            dico_ferm = formulaire["com_ferm"]   # dico fermé du formulaire
            # cumul des scores pour questions fermées
            if nb_questions_ferm > 0:
                points_q1 = points_q1 + dico_ferm["1"][1]  # cumul 1ere question    mini = 0, max = 5
            if nb_questions_ferm > 1:
                points_q2 = points_q2 + dico_ferm["2"][1]  # cumul 2eme question
            if nb_questions_ferm > 2:
                points_q3 = points_q3 + dico_ferm["3"][1]  # cumul 3eme question
            if nb_questions_ferm > 3:
                points_q4 = points_q4 + dico_ferm["4"][1]  # cumul 4eme question
            if nb_questions_ferm > 4:
                points_q5 = points_q5 + dico_ferm["5"][1]  # cumul 5eme question
            if nb_questions_ferm > 5:   
                points_q6 = points_q6 + dico_ferm["6"][1]  # cumul 6eme question
            if nb_questions_ferm > 6:
                points_q7 = points_q7 + dico_ferm["7"][1]  # cumul 7eme question
            if nb_questions_ferm > 7:
                points_q8 = points_q8 + dico_ferm["8"][1]  # cumul 8eme question
            if nb_questions_ferm > 8:
                points_q9 = points_q9 + dico_ferm["9"][1]  # cumul 9eme question
            if nb_questions_ferm > 9:
                points_q10 = points_q10 + dico_ferm["10"][1]  # cumul 10eme question
            
            # cumul des réponses pour questions ouvertes
            dico_ouv = formulaire["com_ouv"]   # dico fermé du formulaire
            if nb_questions_ouvertes > 0:
                question_ouv1 = dico_ouv["1"][0]
                rep_ouv1 = rep_ouv1 + "\n" + dico_ouv["1"][1]
            if nb_questions_ouvertes > 1:
                question_ouv2 = dico_ouv["2"][0]
                rep_ouv2 = rep_ouv2 + "\n" + dico_ouv["2"][1]
            if nb_questions_ouvertes > 2:
                question_ouv3 = dico_ouv["3"][0]
                rep_ouv3 = rep_ouv3 + "\n" + dico_ouv["3"][1]
            if nb_questions_ouvertes > 3:
                question_ouv4 = dico_ouv["4"][0]
                rep_ouv4 = rep_ouv4 + "\n" + dico_ouv["4"][1]   
            if nb_questions_ouvertes > 4:
                question_ouv5 = dico_ouv["5"][0]
                rep_ouv5 = rep_ouv5 + "\n" + dico_ouv["5"][1]
            if nb_questions_ouvertes > 5:
                question_ouv6 = dico_ouv["6"][0]
                rep_ouv6 = rep_ouv6 + "\n" + dico_ouv["6"][1]
            if nb_questions_ouvertes > 6:
                question_ouv7 = dico_ouv["7"][0]
                rep_ouv7 = rep_ouv7 + "\n" + dico_ouv["7"][1]
            if nb_questions_ouvertes > 7:
                question_ouv8 = dico_ouv["8"][0]
                rep_ouv8 = rep_ouv8 + "\n" + dico_ouv["8"][1]
            if nb_questions_ouvertes > 8:
                question_ouv9 = dico_ouv["9"][0]
                rep_ouv9 = rep_ouv9 + "\n" + dico_ouv["9"][1]
            if nb_questions_ouvertes > 9:
                question_ouv10 = dico_ouv["10"][0]
                rep_ouv10 = rep_ouv10 + "\n" + dico_ouv["10"][1]
                
        # fin de boucle questions fermées, calcul des pourcentages
        pourcent_q1 = round((points_q1 / max_points_ferm) * 100)
        pourcent_q2 = round((points_q2 / max_points_ferm) * 100)
        pourcent_q3 = round((points_q3 / max_points_ferm) * 100)
        pourcent_q4 = round((points_q4 / max_points_ferm) * 100)
        pourcent_q5 = round((points_q5 / max_points_ferm) * 100)
        pourcent_q6 = round((points_q6 / max_points_ferm) * 100)
        pourcent_q7 = round((points_q7 / max_points_ferm) * 100)
        pourcent_q8 = round((points_q8 / max_points_ferm) * 100)
        pourcent_q9 = round((points_q9 / max_points_ferm) * 100)
        pourcent_q10 = round((points_q10 / max_points_ferm) * 100)
        # pour chq question, détermination des couleurs d'affichage en fonction du pourcent
        nom_couleur1 = self.couleurs(pourcent_q1)
        nom_couleur2 = self.couleurs(pourcent_q2)
        nom_couleur3 = self.couleurs(pourcent_q3)
        nom_couleur4 = self.couleurs(pourcent_q4)
        nom_couleur5 = self.couleurs(pourcent_q5)
        nom_couleur6 = self.couleurs(pourcent_q6)
        nom_couleur7 = self.couleurs(pourcent_q7)
        nom_couleur8 = self.couleurs(pourcent_q8)
        nom_couleur9 = self.couleurs(pourcent_q9)
        nom_couleur10 = self.couleurs(pourcent_q10)
        self.label_1.background = nom_couleur1
        self.label_2.background = nom_couleur2
        self.label_3.background = nom_couleur3
        self.label_4.background = nom_couleur4
        self.label_5.background = nom_couleur5
        self.label_6.background = nom_couleur6
        self.label_7.background = nom_couleur7
        self.label_8.background = nom_couleur8
        self.label_9.background = nom_couleur9
        self.label_10.background = nom_couleur10
        
        # affichage des formes fermées  en fonction de leur nb
        if nb_questions_ferm > 0:  # Check du nb de questions fermées à afficher et affectation des questions
            self.column_panel_1.visible = True
            self.label_1.text = dico_q_ferm["1"][0] + "        " + str(pourcent_q1) + " %"  # Je prends le 1er elmt de la liste (la question), le 2eme: si question 'obligatoire / facultative'
        if nb_questions_ferm > 1:
            self.column_panel_2.visible = True
            self.label_2.text = dico_q_ferm["2"][0] + "        " + str(pourcent_q2) + " %" 
        if nb_questions_ferm > 2:
            self.column_panel_3.visible = True
            self.label_3.text = dico_q_ferm["3"][0] + "        " + str(pourcent_q3) + " %" 
        if nb_questions_ferm > 3:
            self.column_panel_4.visible = True
            self.label_4.text = dico_q_ferm["4"][0] + "        " + str(pourcent_q4) + " %" 
        if nb_questions_ferm > 4:
            self.column_panel_5.visible = True
            self.label_5.text = dico_q_ferm["5"][0] + "        " + str(pourcent_q5) + " %" 
        if nb_questions_ferm > 5:
            self.column_panel_6.visible = True
            self.label_6.text = dico_q_ferm["6"][0] + "        " + str(pourcent_q6) + " %" 
        if nb_questions_ferm > 6:
            self.column_panel_7.visible = True
            self.label_7.text = dico_q_ferm["7"][0] + "        " + str(pourcent_q7) + " %" 
        if nb_questions_ferm > 7:
            self.column_panel_8.visible = True
            self.label_8.text = dico_q_ferm["8"][0] + "        " + str(pourcent_q8) + " %" 
        if nb_questions_ferm > 8:
            self.column_panel_9.visible = True
            self.label_9.text = dico_q_ferm["9"][0] + "        " + str(pourcent_q9) + " %" 
        if nb_questions_ferm > 9:
            self.column_panel_10.visible = True
            self.label_10.text = dico_q_ferm["10"][0] + "        " + str(pourcent_q10) + " %" 

        # affichage des formes ouvertes en fonction de leur nb
        if nb_questions_ouvertes > 0:
            self.column_panel_a1.visible = True
            self.label_a1.text = question_ouv1
            self.text_area_a1.text = rep_ouv1
            
        if nb_questions_ouvertes > 1:
            self.column_panel_a2.visible = True
            self.label_a2.text = question_ouv2
            self.text_area_a2.text = rep_ouv2
            
        if nb_questions_ouvertes > 2:
            self.column_panel_a3.visible = True
            self.label_a3.text = question_ouv3
            self.text_area_a3.text = rep_ouv3
            
        if nb_questions_ouvertes > 3:
            self.column_panel_a4.visible = True
            self.label_a4.text = question_ouv4
            self.text_area_a4.text = rep_ouv4
        
        if nb_questions_ouvertes > 4:
            self.column_panel_a5.visible = True
            self.label_a5.text = question_ouv5
            self.text_area_a5.text = rep_ouv5
            
        if nb_questions_ouvertes > 5:
            self.column_panel_a6.visible = True
            self.label_a6.text = question_ouv6
            self.text_area_a6.text = rep_ouv6
            
        if nb_questions_ouvertes > 6:
            self.column_panel_a7.visible = True
            self.label_a7.text = question_ouv7
            self.text_area_a7.text = rep_ouv7
        
        if nb_questions_ouvertes > 7:
            self.column_panel_a8.visible = True
            self.label_a8.text = question_ouv8
            self.text_area_a8.text = rep_ouv8
        
        if nb_questions_ouvertes > 8:
            self.column_panel_a9.visible = True
            self.label_a9.text = question_ouv9
            self.text_area_a9.text = rep_ouv9
        
        if nb_questions_ouvertes > 9:
            self.column_panel_a10.visible = True
            self.label_a10.text = question_ouv10
            self.text_area_a10.text = rep_ouv10

        # sauvegarde ds table com si pas déjà sauvegardée. (stage, date et user existant ds table 'com_sum')
        # lecture de table 'com_sum'
        row = app_tables.com_sum.search(stage = stage_row,
                                        user = self.user,
                                        date = self.com_row["date"])
        if len(row) == 0:                                               # Si pas de résultat: pas encore sauvée
            result = anvil.server.call("add_com_results",
                                stage_row,               # row
                                stage_row["numero"],     # num txt
                                self.user,               #user_row
                                self.user["nom"],        # nom (utile pour tri sur nom)
                                self.com_row["date"],    # text
                                pourcent_q1,           # numérique
                                pourcent_q2,           # numérique
                                pourcent_q3,           # numérique
                                pourcent_q4,           # numérique
                                pourcent_q5,           # numérique
                                pourcent_q6,           # numérique
                                pourcent_q7,           # numérique
                                pourcent_q8,           # numérique
                                pourcent_q9,           # numérique
                                pourcent_q10,          # numérique
                                cadre,                 # text
                                dico_q_ferm["1"][0],     # question 1 txt        
                                dico_q_ferm["2"][0],     # question 1 txt        
                                dico_q_ferm["3"][0],     # question 1 txt        
                                dico_q_ferm["4"][0],     # question 1 txt        
                                dico_q_ferm["5"][0],     # question 1 txt        
                                dico_q_ferm["6"][0],     # question 1 txt        
                                dico_q_ferm["7"][0],     # question 1 txt        
                                dico_q_ferm["8"][0],     # question 1 txt        
                                dico_q_ferm["9"][0],     # question 1 txt        
                                dico_q_ferm["10"][0]     # question 1 txt         
                            )
            if result is False:
                alert("Erreur en sauvegarde du récap en table 'com_sum' ")
            else:
                alert("Sauvegarde effectuée")
        else:
            alert("Déjà sauvegardée !")
    
    def couleurs(self, pourcent,  **event_args):    
        if pourcent<=16: 
            nom_couleur = "theme:Error"
        if pourcent<=32 and pourcent > 16: 
            nom_couleur = "theme:Orange"
        if pourcent<=48 and pourcent > 32: 
            nom_couleur = "theme:Jaune Orange"
        if pourcent<=64 and pourcent > 48: 
            nom_couleur = "theme:Vert Tres Clair"
        if pourcent<=80 and pourcent > 64: 
            nom_couleur = "theme:Vert Clair"
        if pourcent > 80: 
            nom_couleur = "theme:Vert Foncé"
        return nom_couleur
        
