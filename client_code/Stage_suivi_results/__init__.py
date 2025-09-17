from ._anvil_designer import Stage_suivi_resultsTemplate
from anvil import *

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Stage_suivi_histograms import (Stage_suivi_histograms)  # Forme ajoutée pour questions fermées histogrammes (add component)
from .Stage_suivi_rep_ouvertes import (Stage_suivi_rep_ouvertes)   #  Forme ajoutée pour questions ouvertes
#import fast_pdf


class Stage_suivi_results(Stage_suivi_resultsTemplate):
    def __init__(self, type_suivi="", pdf_mode=False, row=None, **properties):  # si pdf=True, cette forme  appellée par pdf renderer
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.pdf_mode = pdf_mode     # si on vient du BG task pour génération du pdf, pdf_mode = True
        self.type_suivi = type_suivi # si on vient du BG task pour génération du pdf, rappel quel suivi est demandé, Stagiaire ou Tuteur
        self.column_panel_mailing.visible = False
        
        # import anvil.js    # pour screen size
        from anvil.js import window  # to gain access to the window object
        global screen_size
        screen_size = window.innerWidth

        global cpt
        cpt = 0

        # sélection des stages visualisés ds dropdown (si la saisie du formulaire a été authorisée (table 'stages': saisie_suivi_ok=True))
        liste_stage_drop_down = []
        liste_stages = app_tables.stages.search(
            tables.order_by("numero", ascending=False),
            saisie_suivi_ok=True
        )
        
        # initialistaion de la drop down codes stagiaires
        for stage in liste_stages:
            row_stage = app_tables.stages.get(numero=int(stage["numero"]))
            if row_stage and row_stage["type_stage"] != 'T':   # ne pas inclure ds drop down stgiaires le 'stage' tuteur
                    liste_stage_drop_down.append(
                        (
                            row_stage["code_txt"] + " du " + str(row_stage["date_debut"]),
                            row_stage   # stage normal
                        )
                    )
        self.drop_down_code_stagiaires.items = liste_stage_drop_down
        
        # initialistaion de la drop down codes suivi des tuteurs
        self.drop_down_code_tuteurs.items = liste_stage_drop_down

        # si génération du pdf, on cache des boutons et on envoi directement en traitement en fonction du type de suivi demandé
        if self.pdf_mode is True:
            self.column_panel_a.visible = False
            self.button_annuler2.visible = False
            self.button_downl_pdf1.visible = False
            self.button_downl_pdf0.visible = False

            # exécution automatique, simulation de la sélection du stage en drop down 
            if self.type_suivi == "S":
                self.drop_down_code_stagiaires_change(row)   # row envoyé par la bg task 
            else:  # Tuteurs
                self.drop_down_code_tuteurs_change(row)      # row envoyé par la bg task 
    
    # si row not None, Cette forme est ouverte en appel du pdf renderer, j'ai déjà le row du stage
    def drop_down_code_stagiaires_change(self, row=None ,**event_args):
        """This method is called when an item is selected"""
        self.type_de_suivi = "S"
        self.label_type_suivi.text = "S"  # pour get_open_form en ItemTemplate17
        if row is None:
            row = self.drop_down_code_stagiaires.selected_value
            if row is None: 
                alert("Vous devez sélectionner un stage !")
                self.drop_down_code_stagiaires.focus()
                return
        self.traitement(self.type_de_suivi,row)
        
    # si row not None, Cette forme est ouverte en appel du pdf renderer, j'ai déjà le row du stage
    def drop_down_code_tuteurs_change(self, row=None, **event_args):  # row vient du bg task
        """This method is called when an item is selected"""
        self.type_de_suivi = "T"   
        self.label_type_suivi.text = "T"     # pour get_open_form en ItemTemplate17
        
        if row is None:
            row = self.drop_down_code_tuteurs.selected_value
            self.row = self.drop_down_code_tuteurs.selected_value
            if row is None: 
                alert("Vous devez sélectionner un stage !")
                self.drop_down_code_tuteurs.focus()
                return
        self.traitement(self.type_de_suivi,row)

        
    def traitement(self, type_de_suivi, row):
        self.row = row
        self.type_de_suivi = type_de_suivi
        """ ------------------------------------------------------------------------
                    INITIALISATION DE LA LISTE DES NON REPONSES (pour 'repeating_panel_no_response')
        """
        if type_de_suivi == "S":   # Stagiaires du stage sélectionné 
            self.label_titre_no_response.text = "Stagiaires n'ayant pas encore répondu"
            self.liste_no_response = app_tables.stagiaires_inscrits.search(
                                                                            numero=self.row["numero"],
                                                                            enquete_suivi=False                   
                                                                        )
        if type_de_suivi == "T":   # stage 'Tuteurs'                           !!!!  ATTENTION QD IL Y AURA PLUSIEURS FORMUL 
            self.label_titre_no_response.text = "Tuteurs n'ayant pas encore répondu"
            # liste des tuteurs n'ayant pas remplis leurs Formulaires
            self.liste_no_response = app_tables.stagiaires_inscrits.search(
                                                                            pour_stage_num=self.row,   # colonne spéciale ds table stagiaires inscrits, tuteur ou formateur pour stage ...
                                                                            enquete_suivi=False                   
                                                                        )
            
        if self.liste_no_response:  # retardataires
            self.repeating_panel_no_response.items = self.liste_no_response
            self.column_panel_mailing.visible = True
            if len(self.liste_no_response) > 1:  # plusieurs retardataires
                self.button_mailing_to_all.visible = True
        else:  # pas de retardataires
            self.label_titre_no_response.visible = False
            self.repeating_panel_no_response.visible = False
        # ------------------------------------------------------------------------
        if type_de_suivi == "T":
            self.drop_down_code_stagiaires.visible = False
            text1 = "Tuteurs du "
        else:
            text1 = "Stagiaires du "
            self.drop_down_code_tuteurs.visible = False
            
        self.label_titre.text = (
            text1
            + "Stage n°"
            + str(row["numero"])
            + " "
            + row["code_txt"]
            + " du "
            + str(row["date_debut"])
        )
        self.column_panel_titres.visible = True
        self.drop_down_code_stagiaires.visible = False
        self.column_panel_header.visible = False
        dico_rep_ferm = {}
        dico_rep_ouv = {}

        # Création des dico des réponses cumulées
        rep0_cumul = {}
        rep0_cumul["1"] = (
            0  # Cumul des réponses 0, question 1   # Cumil Réponses 0 pour question 1
        )
        rep0_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep0_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep0_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep0_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep0_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep0_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep0_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep0_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep0_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep1_cumul = {}  # Cumul Réponses 1 pour question 2
        rep1_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep1_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep1_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep1_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep1_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep1_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep1_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep1_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep1_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep1_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep2_cumul = {}  # Cumul Réponses 2
        rep2_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep2_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep2_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep2_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep2_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep2_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep2_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep2_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep2_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep2_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep3_cumul = {}  # Cumil Réponses 3
        rep3_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep3_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep3_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep3_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep3_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep3_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep3_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep3_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep3_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep3_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep4_cumul = {}  # Cumul Réponses 4
        rep4_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep4_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep4_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep4_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep4_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep4_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep4_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep4_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep4_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep4_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep5_cumul = {}  # Cumul Réponses 5
        rep5_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep5_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep5_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep5_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep5_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep5_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep5_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep5_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep5_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep5_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep6_cumul = {}  # Cumul Réponses 6
        rep6_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep6_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep6_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep6_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep6_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep6_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep6_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep6_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep6_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep6_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep7_cumul = {}  # Cumul Réponses 7
        rep7_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep7_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep7_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep7_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep7_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep7_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep7_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep7_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep7_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep7_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep8_cumul = {}  # Cumul Réponses 8
        rep8_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep8_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep8_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep8_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep8_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep8_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep8_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep8_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep8_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep8_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep9_cumul = {}  # Cumul Réponses 9
        rep9_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep9_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep9_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep9_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep9_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep9_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep9_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep9_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep9_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep9_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # Création des dico des réponses cumulées
        rep10_cumul = {}  # Cumul Réponses 10
        rep10_cumul["1"] = 0  # Cumul des réponses 0, question 1
        rep10_cumul["2"] = 0  # Cumul des réponses 0, question 2
        rep10_cumul["3"] = 0  # Cumul des réponses 0, question 3
        rep10_cumul["4"] = 0  # Cumul des réponses 0, question 4
        rep10_cumul["5"] = 0  # Cumul des réponses 0, question 5
        rep10_cumul["6"] = 0  # Cumul des réponses 0, question 6
        rep10_cumul["7"] = 0  # Cumul des réponses 0, question 7
        rep10_cumul["8"] = 0  # Cumul des réponses 0, question 8
        rep10_cumul["9"] = 0  # Cumul des réponses 0, question 9
        rep10_cumul["10"] = 0  # Cumul des réponses 0, question 10

        # lecture des formulaires du stage choisi
        if type_de_suivi == "S":
            liste_formulaires = app_tables.stage_suivi.search(
                                                                stage_num_txt= str(self.row['numero']),   # -------------------------------------   A MODIFIER
                                                                user_role = 'S'        # "T" si sélection Tuteurs ds drop down sinon "S"
                                                            )
        if type_de_suivi == "T":
            liste_formulaires = app_tables.stage_suivi.search(
                                                                stage_num_txt= str(self.row['numero']),   # -------------------------------------   A MODIFIER
                                                                user_role = 'T'        # "T" si sélection Tuteurs ds drop down sinon "S"
                                                            )
        print(len(liste_formulaires), "formulaires de suivi à traiter en 'Stage suivi result, ligne 253'")
        
        cpt_formulaire = 0
        for formulaire in liste_formulaires:
            date = formulaire["date_heure"]
            cpt_formulaire += 1
            print("==========================FORMULAIRE", cpt_formulaire)

            # dico questions fermées
            dico_rep_ferm = formulaire["rep_dico_rep_ferm"]  # dico questions fermées du formulaire
            nb_questions_ferm = len(dico_rep_ferm)  # nb questions ds formulaire questions fermées
            print("nb_q_fermées: ", nb_questions_ferm)

            # dico questions ouvertes
            dico_rep_ouv = formulaire["rep_dico_rep_ouv"]  # dico questions ouvertes du formulaire
            nb_questions_ouv = len(dico_rep_ouv)
            print("nb_q_ouvertes: ", nb_questions_ouv)

            # Boucle sur le dictionaire fermé du formulaire
            # ex du contenu du dico en table qd lu:   ('1', ["Conditions d'accueil sur les lieux de formation:", 0])
            #                                          cle   valeur
            #                             indices valeur;    0                                                    1
            #                                                tuple [question, reponse]
            for cle, val in dico_rep_ferm.items():
                reponse = val[1]  # indice 1: donc reponse (int)

                for q in range(1, nb_questions_ferm + 1):  # boucle sur nb questionsfermées de 1 à nb_questions_fermées (exclusif)
                    question = str(q)  # transorme q (int) en question str
                    # print("======= QUESTION N° ", question)
                    if cle == question:  # ex si question 1
                        print("cle/question: ", cle)
                        print("valeur/reponse: ", reponse)
                        if reponse == 0:  # le stagiaire a répondu 0 à la question
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep0_cumul[str(question)])
                            temp += 1  # cumul de la reponse 0    à la question
                            rep0_cumul[str(question)] = temp
                            print(rep0_cumul[str(question)])
                        if reponse == 1:  # le stagiaire a répondu 1 à la question
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep1_cumul[str(question)])
                            temp += 1  # cumul de la reponse 1    à la question
                            rep1_cumul[str(question)] = temp
                            print(rep1_cumul[str(question)])
                        if reponse == 2:  # le stagiaire a répondu 2 à la question
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep2_cumul[str(question)])
                            temp += 1  # cumul de la reponse 2    à la question
                            rep2_cumul[str(question)] = temp
                            print(rep2_cumul[str(question)])
                        if reponse == 3:  # le stagiaire a répondu 3 à la question
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep3_cumul[str(question)])
                            temp += 1  # cumul de la reponse 3    à la question
                            rep3_cumul[str(question)] = temp
                            print(rep3_cumul[str(question)])
                        if reponse == 4:  # le stagiaire a répondu 4 à la question
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep4_cumul[str(question)])
                            temp += 1  # cumul de la reponse 3    à la question
                            rep4_cumul[str(question)] = temp
                            print(rep4_cumul[str(question)])
                        if reponse == 5:  # le stagiaire a répondu 5 à la question
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep5_cumul[str(question)])
                            temp += 1  # cumul de la reponse 3    à la question
                            rep5_cumul[str(question)] = temp
                            print("cumul5 ", rep5_cumul[str(question)])
       

        # à partir du dico  j'extrais les questions pour les afficher
        cpt_questions = 0
        for cle, val in dico_rep_ferm.items():
            cpt_questions += 1
            qt = val[0]  # indice 0: donc question
            if cpt_questions == 1:
                r0 = rep0_cumul["1"]
                r1 = rep1_cumul["1"]
                r2 = rep2_cumul["1"]
                r3 = rep3_cumul["1"]
                r4 = rep4_cumul["1"]
                r5 = rep5_cumul["1"]
            if cpt_questions == 2:
                r0 = rep0_cumul["2"]
                r1 = rep1_cumul["2"]
                r2 = rep2_cumul["2"]
                r3 = rep3_cumul["2"]
                r4 = rep4_cumul["2"]
                r5 = rep5_cumul["2"]
            if cpt_questions == 3:
                r0 = rep0_cumul["3"]
                r1 = rep1_cumul["3"]
                r2 = rep2_cumul["3"]
                r3 = rep3_cumul["3"]
                r4 = rep4_cumul["3"]
                r5 = rep5_cumul["3"]
            if cpt_questions == 4:
                r0 = rep0_cumul["4"]
                r1 = rep1_cumul["4"]
                r2 = rep2_cumul["4"]
                r3 = rep3_cumul["4"]
                r4 = rep4_cumul["4"]
                r5 = rep5_cumul["4"]
            if cpt_questions == 5:
                r0 = rep0_cumul["5"]
                r1 = rep1_cumul["5"]
                r2 = rep2_cumul["5"]
                r3 = rep3_cumul["5"]
                r4 = rep4_cumul["5"]
                r5 = rep5_cumul["5"]
            if cpt_questions == 6:
                r0 = rep0_cumul["6"]
                r1 = rep1_cumul["6"]
                r2 = rep2_cumul["6"]
                r3 = rep3_cumul["6"]
                r4 = rep4_cumul["6"]
                r5 = rep5_cumul["6"]
            if cpt_questions == 7:
                r0 = rep0_cumul["7"]
                r1 = rep1_cumul["7"]
                r2 = rep2_cumul["7"]
                r3 = rep3_cumul["7"]
                r4 = rep4_cumul["7"]
                r5 = rep5_cumul["7"]
            if cpt_questions == 8:
                r0 = rep0_cumul["8"]
                r1 = rep1_cumul["8"]
                r2 = rep2_cumul["8"]
                r3 = rep3_cumul["8"]
                r4 = rep4_cumul["8"]
                r5 = rep5_cumul["8"]
            if cpt_questions == 9:
                r0 = rep0_cumul["9"]
                r1 = rep1_cumul["9"]
                r2 = rep2_cumul["9"]
                r3 = rep3_cumul["9"]
                r4 = rep4_cumul["9"]
                r5 = rep5_cumul["9"]
            if cpt_questions == 10:
                r0 = rep0_cumul["10"]
                r1 = rep1_cumul["10"]
                r2 = rep2_cumul["10"]
                r3 = rep3_cumul["10"]
                r4 = rep4_cumul["10"]
                r5 = rep5_cumul["10"]

            self.rich_text_info.content = f"Enquête lancée le {date}\nsur {len(liste_formulaires)} formulaires."
            self.column_panel_content.visible = True
            self.column_panel_content.add_component(
                Stage_suivi_histograms(qt, r0, r1, r2, r3, r4, r5)
            )
       

        # =================================================================================================
        # affichage des réponses OUVERTES pour chaque Tuteur
        # =================================================================================================
        # ECRITURE DS FICHIER TEMP DU TYPE DE SUIVI (en bg task, je ne pourrai pas utiliser get_open_formen template17)
        anvil.server.call('temp_type_suivi', type_de_suivi)   # pour récupérer le type de suivi en template 17
        
        # Initialisation 
        if type_de_suivi == "S":
            # Préparation du column panel des noms des stagiaires
            self.liste_noms = app_tables.stagiaires_inscrits.search(
                                                        tables.order_by("name", ascending=True),
                                                        numero=self.row["numero"],                   # CRITERE DIFFERENT, COLONE DIFFERENTE QUE POUR TUTEURS
                                                        enquete_suivi=True   # Enquete_suivi ds  table stagiaires_inscrits
                                                        )
        if type_de_suivi == "T":
            # Préparation du column panel des noms des Tuteurs
            print("tuteur : ", self.row['numero'])
            self.liste_noms = app_tables.stagiaires_inscrits.search(
                                                            tables.order_by("name", ascending=True),
                                                            pour_stage_num=self.row,                     # CRITERE DIFFERENT, COLONE DIFFERENTE QUE POUR STAGIAIRE
                                                            enquete_suivi=True   # Enquete_suivi ds  table stagiaires_inscrits
                                                        )
        print("stage suivi result ligne 499, nb de noms: ", len(self.liste_noms))              # TROUVER ERREUR: self.row ?
        self.repeating_panel_noms.items = self.liste_noms
        
         # Initialisation des clefs: valeur du dictionnaire des réponses
        q_rep = {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
            "5": [],  # cle: num_question   valeur: liste [] des réponses ouvertes pour cette question
            "6": [],
            "7": [],
            "8": [],
            "9": [],
            "10": [],
        }
        # Boucle sur le dictionaire des questions/réponses
        for cle_num_question, val in q_rep.items():
            nb_reponses = (len(val) - 1)  # nb d'éléments - 1 (le 1er élément (la question))
            try:
                qt = val[0]  # question (1er élément)
                # Boucle sur les réponses pour création de la liste des reponses de la question
                liste_rep = []
                for x in range(1, nb_reponses + 1):  # 0:question, 1,2,3 ... les réponses
                    liste_rep.append(val[x])
                #self.column_panel_q_ouv.visible = True
                self.column_panel_q_ouv.add_component(Stage_suivi_rep_ouvertes(qt, liste_rep))
            except:
                pass
        
        
        """ ============================================================================================= FIN DE L'AFFICHAGE DU RESULTAT GLOBAL des Q Fermées"""
        # Génération du pdf A CHANGER QD L'ENQUETE EST COMPLETE
        print("génération du pdf")
        self.button_downl_pdf1.visible = True
        self.button_downl_pdf0.visible = True
        """
        if self.pdf_mode is False:
            with anvil.server.no_loading_indicator:
                self.task_suivi = anvil.server.call('run_bg_task_suivi', type_de_suivi, row["numero"],row["code_txt"], row)
                self.timer_1.interval=0.5
        """
        
    def timer_1_tick(self, **event_args):
        """This method is called Every 0.5 seconds. Does not trigger if [interval] is 0."""
        if self.task_suivi.is_completed():
            self.button_downl_pdf0.visible = True
            self.button_downl_pdf1.visible = True
            self.timer_1.interval=0
            anvil.server.call('task_killer',self.task_suivi)
        

    def button_downl_pdf1_click(self, **event_args):
        """This method is called when the button is clicked"""

        """
        stage_row = app_tables.stages.get(numero=self.row["numero"])
        pdf = stage_row["suivi_pdf"]
        """
        pdf = anvil.server.call('enquete_suivi_pdf_gen', self.row, self.type_de_suivi)
        file_name=(f"Suivi {self.row['code_txt']} stage num {self.row['numero']}")
        
        new_file_named = anvil.BlobMedia("application/pdf", pdf.get_bytes(), name=file_name+".pdf")
        if new_file_named:
            anvil.media.download(new_file_named)
            alert("Enquête téléchargée")
        else:
            alert("Pdf non généré")
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form("Main", 99)

    def button_mailing_to_all_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Transformation de la liste "self.liste_no_response" (stagiaires inscrits) en liste de table user
        liste_email = []
        for stagiaire in self.liste_no_response:
            # lecture table user
            liste_email.append(
                (
                    stagiaire["user_email"]["email"],
                    stagiaire["user_email"]["prenom"],
                    "",
                )
            )  # 3 infos given "" indique qu'il n'y a pas d'id (cas des old stgiares)

        # 'formul' indique l'origine, ici 'formulaire de satisfaction'
        open_form("Mail_subject_attach_txt", liste_email, "formul")


       
