from ._anvil_designer import Stage_satisf_statisticsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Stage_satisf_histograms import Stage_satisf_histograms   # Forme ajoutée pour questions fermées histogrammes (add component) 
from .Stage_satisf_rep_ouvertes import Stage_satisf_rep_ouvertes  #  Forme ajoutée pour questions ouvertes
#import fast_pdf

class Stage_satisf_statistics(Stage_satisf_statisticsTemplate):
    def __init__(self,pdf_mode=False, row=None, **properties):  # si pdf=True, cette forme  appellée par pdf renderer  
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.column_panel_mailing.visible = False
        # Any code you write here will run before the form opens.
        self.pdf_mode = pdf_mode    # appel du pdf renderer ?
        self.timer_1.interval=0     # neutralise le timer
        self.test_existence_pdf = False
        # import anvil.js    # pour screen size
        from anvil.js import window  # to gain access to the window object

        global screen_size
        screen_size = window.innerWidth

        global cpt
        cpt = 0   
        if self.pdf_mode is True:
            self.column_panel_a.visible = False
            self.button_annuler2.visible = False
            self.button_downl_pdf1.visible = False
            self.drop_down_code_stages_change(row)
        
        # sélection des stages si la saisie du formulaire a été validée (saisie_satisf_ok=True)
        liste_stage_drop_down =[]
        liste_stages = app_tables.stages.search(tables.order_by("numero", ascending=False),
                                                saisie_satisf_ok=True)
        # création de la drop down codes stages 
        for stage in liste_stages:
            row_stage = app_tables.stages.get(numero=int(stage['numero']))
            if row_stage:
                liste_stage_drop_down.append((row_stage["code_txt"]+" du "+str(row_stage["date_debut"]),row_stage))
        self.drop_down_code_stages.items = liste_stage_drop_down
        
    # si row not None, Cette forme est ouverte en appel du pdf renderer, j'ai déjà le row du stage
    def drop_down_code_stages_change(self, row=None,**event_args):
        """This method is called when an item is selected"""
        if row is None:   # *********************************************** A TESTER
            row = self.drop_down_code_stages.selected_value  # row du stage sélectionné ds le drop down
        if row is None:
            alert("Vous devez sélectionner un stage !")
            self.drop_down_code_stage.focus()
            return
        self.row = row

        """ ------------------------------------------------------------------------
                    INITIALISATION DE LA LISTE DES NON REPONSES (column panel)
        """ 
        self.liste_no_response = app_tables.stagiaires_inscrits.search(
                                                                numero = row["numero"],
                                                                enquete_satisf = False
                                                                )
        if self.liste_no_response:   # retardataires
            self.repeating_panel_no_response.items = self.liste_no_response
            self.column_panel_mailing.visible = True
            if len(self.liste_no_response) > 1:   # plusieurs retardataires
                self.button_mailing_to_all.visible = True
        else:  # pas de retardataires
            self.label_titre_no_response.visible = False
            self.repeating_panel_no_response.visible = False
        # ------------------------------------------------------------------------
        # test si un stagiaire au moins a rempli le formulaire de satisfaction
        liste_test = app_tables.stage_satisf.search(stage_row=row)
        if len(liste_test) == 0:
            return
            
        
        # Si pdf déjà sauvé en table stage, j'affiche les boutons téléchargement et renseigne ma variable de test
        stage_row = app_tables.stages.get(numero=self.row["numero"])
        pdf = stage_row['satis_pdf']
        if pdf and self.pdf_mode is not True:
            self.button_downl_pdf0.visible = True
            self.button_downl_pdf1.visible = True
            self.test_existence_pdf = True
       
        self.label_titre.text = "Stage n°"+str(row["numero"])+" "+row["code_txt"]+" du "+str(row["date_debut"])
        self.column_panel_titres.visible = True
        self.drop_down_code_stages.visible = False
        self.column_panel_header.visible = False
        dico_rep_ferm = {}
        dico_rep_ouv = {}

        # Création des dico des réponses cumulées
        rep0_cumul = {}                                                 
        rep0_cumul["1"] =  0        # Cumul des réponses 0, question 1   # Cumil Réponses 0 pour question 1
        rep0_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep0_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep0_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep0_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep0_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep0_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep0_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep0_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep0_cumul["10"] =  0        # Cumul des réponses 0, question 10   

        # Création des dico des réponses cumulées
        rep1_cumul = {}                                                 # Cumul Réponses 1 pour question 2
        rep1_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep1_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep1_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep1_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep1_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep1_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep1_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep1_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep1_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep1_cumul["10"] =  0        # Cumul des réponses 0, question 10   

        # Création des dico des réponses cumulées
        rep2_cumul = {}                                                 # Cumul Réponses 2
        rep2_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep2_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep2_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep2_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep2_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep2_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep2_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep2_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep2_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep2_cumul["10"] =  0        # Cumul des réponses 0, question 10   
        
         # Création des dico des réponses cumulées
        rep3_cumul = {}                                                 # Cumil Réponses 3
        rep3_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep3_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep3_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep3_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep3_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep3_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep3_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep3_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep3_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep3_cumul["10"] =  0        # Cumul des réponses 0, question 10   

        # Création des dico des réponses cumulées
        rep4_cumul = {}                                                 # Cumul Réponses 4
        rep4_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep4_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep4_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep4_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep4_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep4_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep4_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep4_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep4_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep4_cumul["10"] =  0        # Cumul des réponses 0, question 10   

        # Création des dico des réponses cumulées
        rep5_cumul = {}                                                 # Cumul Réponses 5
        rep5_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep5_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep5_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep5_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep5_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep5_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep5_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep5_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep5_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep5_cumul["10"] =  0        # Cumul des réponses 0, question 10

         # Création des dico des réponses cumulées
        rep6_cumul = {}                                                 # Cumul Réponses 6
        rep6_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep6_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep6_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep6_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep6_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep6_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep6_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep6_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep6_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep6_cumul["10"] =  0        # Cumul des réponses 0, question 10

         # Création des dico des réponses cumulées
        rep7_cumul = {}                                                 # Cumul Réponses 7
        rep7_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep7_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep7_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep7_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep7_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep7_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep7_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep7_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep7_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep7_cumul["10"] =  0        # Cumul des réponses 0, question 10

         # Création des dico des réponses cumulées
        rep8_cumul = {}                                                 # Cumul Réponses 8
        rep8_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep8_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep8_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep8_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep8_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep8_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep8_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep8_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep8_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep8_cumul["10"] =  0        # Cumul des réponses 0, question 10

         # Création des dico des réponses cumulées
        rep9_cumul = {}                                                 # Cumul Réponses 9
        rep9_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep9_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep9_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep9_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep9_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep9_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep9_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep9_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep9_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep9_cumul["10"] =  0        # Cumul des réponses 0, question 10

         # Création des dico des réponses cumulées
        rep10_cumul = {}                                                 # Cumul Réponses 10
        rep10_cumul["1"] =  0        # Cumul des réponses 0, question 1   
        rep10_cumul["2"] =  0        # Cumul des réponses 0, question 2  
        rep10_cumul["3"] =  0        # Cumul des réponses 0, question 3   
        rep10_cumul["4"] =  0        # Cumul des réponses 0, question 4   
        rep10_cumul["5"] =  0        # Cumul des réponses 0, question 5   
        rep10_cumul["6"] =  0        # Cumul des réponses 0, question 6   
        rep10_cumul["7"] =  0        # Cumul des réponses 0, question 7   
        rep10_cumul["8"] =  0        # Cumul des réponses 0, question 8   
        rep10_cumul["9"] =  0        # Cumul des réponses 0, question 9   
        rep10_cumul["10"] = 0        # Cumul des réponses 0, question 10
        
        # lecture des formulaires du stage choisi
        cpt_formulaire = 0
        liste_formulaires = app_tables.stage_satisf.search(stage_row=row)
        print(len(liste_formulaires), 'formulaires à traiter')
        
        for formulaire in liste_formulaires:
            date = formulaire['date_heure']
            cpt_formulaire += 1
            print("==========================FORMULAIRE", cpt_formulaire)

            # dico questions fermées
            dico_rep_ferm = formulaire["rep_dico_rep_ferm"]  # dico questions fermées du formulaire
            nb_questions_ferm = len(dico_rep_ferm) #nb questions ds formulaire questions fermées 
            print("nb_q_fermées: ", nb_questions_ferm)
            
            # dico questions ouvertes
            dico_rep_ouv = formulaire["rep_dico_rep_ouv"]   # dico questions ouvertes du formulaire
            nb_questions_ouv = len(dico_rep_ouv)
            print("nb_q_ouvertes: ", nb_questions_ouv)
            
            # Boucle sur le dictionaire fermé du formulaire
            # ex du contenu du dico en table qd lu:   ('1', ["Conditions d'accueil sur les lieux de formation:", 0])
            #                                          cle   valeur
            #                             indices valeur;    0                                                    1
            #                                                tuple [question, reponse]    
            for cle, val in dico_rep_ferm.items():
                
                reponse = val[1]  # indice 1: donc reponse (int)
                
                for q in range(1,nb_questions_ferm+1): # boucle sur nb questionsfermées de 1 à nb_questions_fermées (exclusif)
                    question = str(q) # transorme q (int) en question str
                    #print("======= QUESTION N° ", question)
                    if cle == question:  # ex si question 1        
                        print("cle/question: ",cle)
                        print("valeur/reponse: ",reponse)
                        if reponse == 0:                                  # le stagiaire a répondu 0 à la question 
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep0_cumul[str(question)])
                            temp += 1    # cumul de la reponse 0    à la question 
                            rep0_cumul[str(question)]=temp
                            print(rep0_cumul[str(question)])
                        if reponse == 1:                                  # le stagiaire a répondu 1 à la question 
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep1_cumul[str(question)])
                            temp += 1    # cumul de la reponse 1    à la question 
                            rep1_cumul[str(question)]=temp
                            print(rep1_cumul[str(question)])     
                        if reponse == 2:                                  # le stagiaire a répondu 2 à la question 
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep2_cumul[str(question)])
                            temp += 1    # cumul de la reponse 2    à la question 
                            rep2_cumul[str(question)]=temp
                            print(rep2_cumul[str(question)]) 
                        if reponse == 3:                                  # le stagiaire a répondu 3 à la question 
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep3_cumul[str(question)])
                            temp += 1    # cumul de la reponse 3    à la question 
                            rep3_cumul[str(question)]=temp
                            print(rep3_cumul[str(question)]) 
                        if reponse == 4:                                  # le stagiaire a répondu 4 à la question 
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep4_cumul[str(question)])
                            temp += 1    # cumul de la reponse 3    à la question 
                            rep4_cumul[str(question)]=temp
                            print(rep4_cumul[str(question)]) 
                        if reponse == 5:                     # le stagiaire a répondu 5 à la question 
                            # lecture dico des cumuls pour la question, réponse 0
                            temp = int(rep5_cumul[str(question)])
                            temp += 1    # cumul de la reponse 3    à la question 
                            rep5_cumul[str(question)]=temp
                            print("cumul5 ", rep5_cumul[str(question)]) 
        """            
        print(f"Résultat pour les {len(liste_formulaires)} formulaires:")  
        print("nb de rep 0/1: ", rep0_cumul["1"])
        print("nb de rep 1/1: ", rep1_cumul["1"])
        print("nb de rep 2/1: ", rep2_cumul["1"])
        print("nb de rep 3/1: ", rep3_cumul["1"])
        print("nb de rep 4/1: ", rep4_cumul["1"])
        print("nb de rep 5/1: ", rep5_cumul["1"])
        print()
        print("nb de rep 0/2: ", rep0_cumul["2"])
        print("nb de rep 1/2: ", rep1_cumul["2"])
        print("nb de rep 2/2: ", rep2_cumul["2"])
        print("nb de rep 3/2: ", rep3_cumul["2"])
        print("nb de rep 4/2: ", rep4_cumul["2"])
        print("nb de rep 5/2: ", rep5_cumul["2"])
        print()
        print("nb de rep 0/3: ", rep0_cumul["3"])
        print("nb de rep 1/3: ", rep1_cumul["3"])
        print("nb de rep 2/3: ", rep2_cumul["3"])
        print("nb de rep 3/3: ", rep3_cumul["3"])
        print("nb de rep 4/3: ", rep4_cumul["3"])
        print("nb de rep 5/3: ", rep5_cumul["3"])
        print()
        print("nb de rep 0/4: ", rep0_cumul["4"])
        print("nb de rep 1/4: ", rep1_cumul["4"])
        print("nb de rep 2/4: ", rep2_cumul["4"])
        print("nb de rep 3/4: ", rep3_cumul["4"])
        print("nb de rep 4/4: ", rep4_cumul["4"])
        print("nb de rep 5/4: ", rep5_cumul["4"])
        print()
        print("nb de rep 0/5: ", rep0_cumul["5"])
        print("nb de rep 1/5: ", rep1_cumul["5"])
        print("nb de rep 2/5: ", rep2_cumul["5"])
        print("nb de rep 3/5: ", rep3_cumul["5"])
        print("nb de rep 4/5: ", rep4_cumul["5"])
        print("nb de rep 5/5: ", rep5_cumul["5"])
        print()
        print("nb de rep 0/6: ", rep0_cumul["6"])
        print("nb de rep 1/6: ", rep1_cumul["6"])
        print("nb de rep 2/6: ", rep2_cumul["6"])
        print("nb de rep 3/6: ", rep3_cumul["6"])
        print("nb de rep 4/6: ", rep4_cumul["6"])
        print("nb de rep 5/6: ", rep5_cumul["6"])
        print()
        print("nb de rep 0/7: ", rep0_cumul["7"])
        print("nb de rep 1/7: ", rep1_cumul["7"])
        print("nb de rep 2/7: ", rep2_cumul["7"])
        print("nb de rep 3/7: ", rep3_cumul["7"])
        print("nb de rep 4/7: ", rep4_cumul["7"])
        print("nb de rep 5/7: ", rep5_cumul["7"])
        print()
        print("nb de rep 0/8: ", rep0_cumul["8"])
        print("nb de rep 1/8: ", rep1_cumul["8"])
        print("nb de rep 2/8: ", rep2_cumul["8"])
        print("nb de rep 3/8: ", rep3_cumul["8"])
        print("nb de rep 4/8: ", rep4_cumul["8"])
        print("nb de rep 5/8: ", rep5_cumul["8"])
        print()
        print("nb de rep 0/9: ", rep0_cumul["9"])
        print("nb de rep 1/9: ", rep1_cumul["9"])
        print("nb de rep 2/9: ", rep2_cumul["9"])
        print("nb de rep 3/9: ", rep3_cumul["9"])
        print("nb de rep 4/9: ", rep4_cumul["9"])
        print("nb de rep 5/9: ", rep5_cumul["9"])
        print()
        print("nb de rep 0/10: ", rep0_cumul["10"])
        print("nb de rep 1/10: ", rep1_cumul["10"])
        print("nb de rep 2/10: ", rep2_cumul["10"])
        print("nb de rep 3/10: ", rep3_cumul["10"])
        print("nb de rep 4/10: ", rep4_cumul["10"])
        print("nb de rep 5/10: ", rep5_cumul["10"])
        """
        
        # à partir du dico  j'extrai les questions pour les afficher 
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

            self.rich_text_info.content = f"Enquête lancée le {date}\nsur {len(liste_formulaires)}  formulaires."
            self.column_panel_content.visible = True
            self.column_panel_content.add_component(Stage_satisf_histograms(qt,r0,r1,r2,r3,r4,r5))
        
        
        #=================================================================================================
        # affichage des réponses OUVERTES pour chaque question
        #=================================================================================================
        # Initialisation des clefs: valeur du dictionnaire des réponses
        q_rep = {"1":[],   
                 "2":[],
                 "3":[],
                 "4":[],
                 "5":[],        # cle: num_question   valeur: liste [] des réponses ouvertes pour cette question
                 "6":[],
                 "7":[],
                 "8":[],
                 "9":[],
                 "10":[]  
                }          
       
        # Boucle sur tous les formulaires du stage
        cpt_formulaire = 0
        for formulaire in liste_formulaires:
            cpt_formulaire += 1
            print("==========================FORMULAIRE", cpt_formulaire)

            # lecture dico questions ouvertes du formulaire
            dico_rep_ouv = formulaire["rep_dico_rep_ouv"]  # dico questions ouvertes du formulaire
            nb_questions_ouv = len(dico_rep_ouv) #nb questions ds formulaire questions fermées 
            print("nb_q_ouvertes: ", nb_questions_ouv)

            # lecture des 10 réponses de ce formulaire
            for cle_num_question,val in dico_rep_ouv.items():
                quest = val[0]
                rep = val[1]
                liste_rep=[]   # liste cumul des réponses d'1 question
                print("===========================  question n° ",cle_num_question )
                print("===========================  question ", quest )
                print(" ========================== rep ", rep)
                print()
                
                #recherche de la clef q_rep déjà constituée
                liste_rep = q_rep[cle_num_question]
            
                # si 1er formulaire, je met les questions ds le dict des reponses q_rep
                if cpt_formulaire == 1:
                    print("-------------------------------------------------------------------------- Ajout de q°", quest )
                    #ajout de la question ds la valeur 
                    liste_rep.append(quest)
                    
                #rajout de la réponse de ce formulaire à la liste de réponses
                try:
                    text_rep = formulaire['nom']+' '+formulaire['prenom']+': '+rep
                except:
                    text_rep = rep      # si le formulaire ancien, anonyme, donc nom et prénom vides
                liste_rep.append(text_rep)
                
                #réecriture de la question et de ses réponses ds le dictionaires des réponses
                q_rep[cle_num_question]=liste_rep

        print(q_rep)
        print()
        print()
        
        # Boucle sur le dictionaire des questions/réponses
        for cle_num_question,val in q_rep.items():
            nb_reponses = len(val)-1  # nb d'éléments - 1 (le 1er élément (la question))
            try:
                qt = val[0]   # question (1er élément) 
                # Boucle sur les réponses pour création de la liste des reponses de la question
                liste_rep = []
                for x in range(1,nb_reponses+1):  # 0:question, 1,2,3 ... les réponses
                    liste_rep.append(val[x])
                self.column_panel_q_ouv.visible=True
                self.column_panel_q_ouv.add_component(Stage_satisf_rep_ouvertes(qt,liste_rep))
            except:
                pass
            
        """ ============================================================================================= FIN DE L'AFFICHAGE DU RESULTAT """
        # Génération du pdf si non existant A CHANGER QD L'ENQUETE EST COMPLETE
        print("génération du pdf")
        #if self.test_existence_pdf is not True or self.test_existence_pdf is True:
        if self.pdf_mode is False:
            with anvil.server.no_loading_indicator:
                self.task_satisf = anvil.server.call('run_bg_task_satisf',row["numero"],row["code_txt"], row)
                self.timer_1.interval=0.5
            
    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.task_satisf.is_completed():
            self.button_downl_pdf0.visible = True
            self.button_downl_pdf1.visible = True
            self.timer_1.interval=0
            anvil.server.call('task_killer',self.task_satisf)

            
    def button_downl_pdf1_click(self, **event_args):
        """This method is called when the button is clicked"""
        stage_row = app_tables.stages.get(numero=self.row["numero"])
        pdf = stage_row['satis_pdf']
        if pdf:
            anvil.media.download(pdf)
            alert("Enquête téléchargée")
        else:
            alert("Pdf non trouvé en table Stages")
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def button_mailing_to_all_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Transformation de la liste "self.liste_no_response" (stagiaires inscrits) en liste de table user 
        liste_email = []
        for stagiaire in self.liste_no_response:
            #lecture table user
            liste_email.append((stagiaire['user_email']['email'],stagiaire['user_email']['prenom'],""))  # 3 infos given "" indique qu'il n'y a pas d'id (cas des old stgiares)
            
        # 'formul' indique l'origine, ici 'formulaire de satisfaction'
        open_form("Mail_subject_attach_txt",  liste_email, 'formul') 
 

    



