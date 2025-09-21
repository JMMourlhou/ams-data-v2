from ._anvil_designer import Stage_form_suiviTemplate
from .. import French_zone  # POur acquisition de date et heure Francaise (Browser time)
from anvil import *

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

global user_row
user_row = None
global stage_row
stage_row = ()
global nb_questions_ferm  # nb questions fermées (check 0 à 5)
nb_questions_ferm = 0
global nb_questions_ouvertes  # nb questions ouvertes
nb_questions_ouvertes = 0
global dico_q_ferm
dico_q_ferm = {}
global dico_q_ouv
dico_q_ouv = {}

class Stage_form_suivi(Stage_form_suiviTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.column_panel_q_ouv.tag = "q_ouvertes"
        self.column_panel_header.tag = "header"
        self.column_panel_0.tag = 0
        self.column_panel_1.tag = 1
        self.column_panel_2.tag = 2
        self.column_panel_3.tag = 3
        self.drop_down_stagiaires.tag= "dropdown"  # je donne un tag quelquonque à la drop down de choix stagiaire si user tuteur ou formateur
        self.column_panel_4.tag = 4
        self.column_panel_5.tag = 5
        self.column_panel_6.tag = 6
        self.column_panel_7.tag = 7
        self.column_panel_8.tag = 8
        self.column_panel_9.tag = 9
        self.column_panel_10.tag = 10
        self.flow_panel_1.tag = "fp"
        self.flow_panel_2.tag = "fp"
        self.flow_panel_3.tag = "fp"
        self.flow_panel_4.tag = "fp"
        self.flow_panel_5.tag = "fp"
        self.flow_panel_6.tag = "fp"
        self.flow_panel_7.tag = "fp"
        self.flow_panel_8.tag = "fp"
        self.flow_panel_9.tag = "fp"
        self.flow_panel_10.tag = "fp"
        self.label_1.tag = "label"
        self.label_2.tag = "label"
        self.label_3.tag = "label"
        self.label_4.tag = "label"
        self.label_5.tag = "label"
        self.label_6.tag = "label"
        self.label_7.tag = "label"
        self.label_8.tag = "label"
        self.label_9.tag = "label"
        self.label_10.tag = "label"

        global user_row
        user_row = anvil.users.get_user()
        if user_row:
            # Drop down stages inscrits du user
            liste0 = app_tables.stagiaires_inscrits.search(
                                                q.fetch_only("user_email", "stage"),  # <----------------------  A Modifier?
                                                user_email=user_row,
                                                #enquete_suivi = False   s  # je permmets plusieurs saisies (pour les tuteurs qui ont plusieurs stgiaires)
                                                             )
            print("nb de stages où le stagiaire est inscrit; ", len(liste0))
            
            liste_drop_d = []
            # si user = stagiaire
            if user_row["role"]=="S":
                for row in liste0:
                    # lecture fichier père stage
                    stage = app_tables.stages.get(numero=row["stage"]["numero"])
                    if (stage["saisie_suivi_ok"] is True):  # si autorisé à saisir le formulaire de suivi, je l'affiche
                        # lecture fichier père type de stage
                        type = app_tables.codes_stages.get(q.fetch_only("code"), code=stage["code"]["code"])
                        if type["type_stage"] == "S":  # Si stagiaire, j'affiche la date
                            liste_drop_d.append((type["code"] + "  du " + str(stage["date_debut"]), stage))
                        else:
                            liste_drop_d.append((type["intitulé"], stage))
                            
            # si c'est un tuteur qui a ouvert, il faut savoir pour quel code stage         
            if user_row["role"]=="T":
                # Drop down stages de BPMotoN 
                # code_moto = app_tables.codes_stages.get(code="BPMOTO")
                liste1 = app_tables.stages.search(
                                                    tables.order_by("date_debut", ascending=False),
                                                    q.any_of(
                                                    q.any_of(code_txt="BPMOTO"),
                                                    q.any_of(code_txt="BPAAN")
                                                    )
                                                   )
                for stage in liste1:
                    if stage["saisie_suivi_ok"] is True:  # si autorisé à saisir le formulaire de suivi, je l'affiche
                        liste_drop_d.append((stage["code"]['code'] + " débuté le " + str(stage["date_debut"]), stage))
                
            # print(liste_drop_d)
            self.drop_down_code_stage.items = liste_drop_d

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form("Main", 99)

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        global stage_row
        stage_row = self.drop_down_code_stage.selected_value
        if stage_row is None:
            alert("Vous devez sélectionner un stage !")
            self.drop_down_code_stage.focus()
            return
            
        # Si c'est un tuteur (ou formateur)    
        """
        if user_row["role"]=="T" or  user_row["role"]=="F": 
            # sélection des stagiaires du stage sélectionné
            liste_stagiaires = app_tables.stagiaires_inscrits.search(tables.order_by("prenom", ascending=True),
                                                                     stage = stage_row
                                                                    )
            print(len(liste_stagiaires))
            # création de la drop down codes stages 
            liste_drop_d_stagiaires = []
            for stagiaire in liste_stagiaires:
                ligne_drop_d_visible = stagiaire["prenom"]+" "+stagiaire["name"]
                liste_drop_d_stagiaires.append((ligne_drop_d_visible, stagiaire['user_email']))
            self.drop_down_stagiaires.items = liste_drop_d_stagiaires
            self.text_area_a3.visible = False
            self.drop_down_stagiaires.visible = True
        """
        self.text_area_a1.text = None
        # extraction des 2 dictionnaires du stage
        global dico_q_ferm
        global dico_q_ouv
        if user_row["role"]=="S":
            dico_q_ferm = stage_row["suivi_dico1_q_ferm"]
            dico_q_ouv = stage_row["suivi_dico2_q_ouv"]  # check du nb de questions ouvertes à afficher et affectation des questions
        else:
            # lecture du template des tuteurs ds table codes_stages
            row_tuteur = app_tables.codes_stages.get(code="T_BASE_N")
            if row_tuteur:
                dico_q_ferm = row_tuteur["suivi_stage_q_ferm_template"]
                dico_q_ouv = row_tuteur["suivi_stage_q_ouv_template"]

        # AFFICHAGE EN FONCTION DU NB DE QUESTIONS
        global nb_questions_ferm  # nb questions fermées (testé en validation)
        nb_questions_ferm = len(dico_q_ferm)  # nb de questions fermées ds le dico
        print(f"{nb_questions_ferm} questions_ferm")
        
        global nb_questions_ouvertes  # nb questions ouvertes
        nb_questions_ouvertes = len(dico_q_ouv)
        print(f"{nb_questions_ouvertes} questions_ouvertes")       

        if nb_questions_ferm > 0:  # Check du nb de questions fermées à afficher et affectation des questions
            self.column_panel_1.visible = True
            self.label_1.text = dico_q_ferm["1"][0]  # Je prends le 1er elmt de la liste (la question), le 2eme: si question 'obligatoire / facultative'
        if nb_questions_ferm > 1:
            self.column_panel_2.visible = True
            self.label_2.text = dico_q_ferm["2"][0]
        if nb_questions_ferm > 2:
            self.column_panel_3.visible = True
            self.label_3.text = dico_q_ferm["3"][0]
        if nb_questions_ferm > 3:
            self.column_panel_4.visible = True
            self.label_4.text = dico_q_ferm["4"][0]
        if nb_questions_ferm > 4:
            self.column_panel_5.visible = True
            self.label_5.text = dico_q_ferm["5"][0]
        if nb_questions_ferm > 5:
            self.column_panel_6.visible = True
            self.label_6.text = dico_q_ferm["6"][0]
        if nb_questions_ferm > 6:
            self.column_panel_7.visible = True
            self.label_7.text = dico_q_ferm["7"][0]
        if nb_questions_ferm > 7:
            self.column_panel_8.visible = True
            self.label_8.text = dico_q_ferm["8"][0]
        if nb_questions_ferm > 8:
            self.column_panel_9.visible = True
            self.label_9.text = dico_q_ferm["9"][0]
        if nb_questions_ferm > 9:
            self.column_panel_10.visible = True
            self.label_10.text = dico_q_ferm["10"][0]
        
        if nb_questions_ouvertes > 0:
            self.column_panel_a1.visible = True
            self.label_a1.text = dico_q_ouv["1"][0]
            if dico_q_ouv["1"][1] == "obligatoire":
                self.text_area_a1.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a1.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 1:
            self.column_panel_a2.visible = True
            self.label_a2.text = dico_q_ouv["2"][0]
            if dico_q_ouv["2"][1] == "obligatoire":
                self.text_area_a2.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a1.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 2:
            self.column_panel_a3.visible = True
            self.label_a3.text = dico_q_ouv["3"][0]
            if dico_q_ouv["3"][1] == "obligatoire":
                self.text_area_a3.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a3.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 3:
            self.column_panel_a4.visible = True
            self.label_a4.text = dico_q_ouv["4"][0]
            if dico_q_ouv["4"][1] == "obligatoire":
                self.text_area_a4.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a4.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 4:
            self.column_panel_a5.visible = True
            self.label_a5.text = dico_q_ouv["5"][0]
            if dico_q_ouv["5"][1] == "obligatoire":
                self.text_area_a5.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a5.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 5:
            self.column_panel_a6.visible = True
            self.label_a6.text = dico_q_ouv["6"][0]
            if dico_q_ouv["6"][1] == "obligatoire":
                self.text_area_a6.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a6.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 6:
            self.column_panel_a7.visible = True
            self.label_a7.text = dico_q_ouv["7"][0]
            if dico_q_ouv["7"][1] == "obligatoire":
                self.text_area_a7.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a7.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 7:
            self.column_panel_a8.visible = True
            self.label_a8.text = dico_q_ouv["8"][0]
            if dico_q_ouv["8"][1] == "obligatoire":
                self.text_area_a8.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a8.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 8:
            self.column_panel_a9.visible = True
            self.label_a9.text = dico_q_ouv["9"][0]
            if dico_q_ouv["9"][1] == "obligatoire":
                self.text_area_a9.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a9.placeholder = "Votre réponse ... (facultative)"
        if nb_questions_ouvertes > 9:
            self.column_panel_a10.visible = True
            self.label_a10.text = dico_q_ouv["10"][0]
            if dico_q_ouv["10"][1] == "obligatoire":
                self.text_area_a10.placeholder = "Votre réponse ... (obligatoire)"
            else:
                self.text_area_a10.placeholder = "Votre réponse ... (facultative)"
        self.button_valider.visible = True

    def check_box_1_1_change(self, **event_args):  # 1 seule réponse doit être checker
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_1_1.checked is True:
            self.check_box_1_2.checked = False
            self.check_box_1_3.checked = False
            self.check_box_1_4.checked = False
            self.check_box_1_5.checked = False
            self.check_box_1_6.checked = False

    def check_box_1_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_1_2.checked is True:
            self.check_box_1_1.checked = False
            self.check_box_1_3.checked = False
            self.check_box_1_4.checked = False
            self.check_box_1_5.checked = False
            self.check_box_1_6.checked = False

    def check_box_1_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_1_3.checked is True:
            self.check_box_1_1.checked = False
            self.check_box_1_2.checked = False
            self.check_box_1_4.checked = False
            self.check_box_1_5.checked = False
            self.check_box_1_6.checked = False

    def check_box_1_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_1_4.checked is True:
            self.check_box_1_1.checked = False
            self.check_box_1_3.checked = False
            self.check_box_1_2.checked = False
            self.check_box_1_5.checked = False
            self.check_box_1_6.checked = False

    def check_box_1_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_1_5.checked is True:
            self.check_box_1_1.checked = False
            self.check_box_1_2.checked = False
            self.check_box_1_4.checked = False
            self.check_box_1_3.checked = False
            self.check_box_1_6.checked = False

    def check_box_1_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_1_6.checked is True:
            self.check_box_1_1.checked = False
            self.check_box_1_2.checked = False
            self.check_box_1_4.checked = False
            self.check_box_1_3.checked = False
            self.check_box_1_5.checked = False

    # ================================================================================= 2eme ligne
    def check_box_2_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_2_1.checked is True:
            self.check_box_2_2.checked = False
            self.check_box_2_3.checked = False
            self.check_box_2_4.checked = False
            self.check_box_2_5.checked = False
            self.check_box_2_6.checked = False

    def check_box_2_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_2_2.checked is True:
            self.check_box_2_1.checked = False
            self.check_box_2_3.checked = False
            self.check_box_2_4.checked = False
            self.check_box_2_5.checked = False
            self.check_box_2_6.checked = False

    def check_box_2_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_2_3.checked is True:
            self.check_box_2_1.checked = False
            self.check_box_2_2.checked = False
            self.check_box_2_4.checked = False
            self.check_box_2_5.checked = False
            self.check_box_2_6.checked = False

    def check_box_2_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_2_4.checked is True:
            self.check_box_2_1.checked = False
            self.check_box_2_3.checked = False
            self.check_box_2_2.checked = False
            self.check_box_2_5.checked = False
            self.check_box_2_6.checked = False

    def check_box_2_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_2_5.checked is True:
            self.check_box_2_1.checked = False
            self.check_box_2_2.checked = False
            self.check_box_2_4.checked = False
            self.check_box_2_3.checked = False
            self.check_box_2_6.checked = False

    def check_box_2_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_2_6.checked is True:
            self.check_box_2_1.checked = False
            self.check_box_2_2.checked = False
            self.check_box_2_4.checked = False
            self.check_box_2_3.checked = False
            self.check_box_2_5.checked = False

    # ================================================================================= 3eme ligne
    def check_box_3_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_3_1.checked is True:
            self.check_box_3_2.checked = False
            self.check_box_3_3.checked = False
            self.check_box_3_4.checked = False
            self.check_box_3_5.checked = False
            self.check_box_3_6.checked = False

    def check_box_3_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_3_2.checked is True:
            self.check_box_3_1.checked = False
            self.check_box_3_3.checked = False
            self.check_box_3_4.checked = False
            self.check_box_3_5.checked = False
            self.check_box_3_6.checked = False

    def check_box_3_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_3_3.checked is True:
            self.check_box_3_1.checked = False
            self.check_box_3_2.checked = False
            self.check_box_3_4.checked = False
            self.check_box_3_5.checked = False
            self.check_box_3_6.checked = False

    def check_box_3_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_3_4.checked is True:
            self.check_box_3_1.checked = False
            self.check_box_3_3.checked = False
            self.check_box_3_2.checked = False
            self.check_box_3_5.checked = False
            self.check_box_3_6.checked = False

    def check_box_3_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_3_5.checked is True:
            self.check_box_3_1.checked = False
            self.check_box_3_2.checked = False
            self.check_box_3_4.checked = False
            self.check_box_3_3.checked = False
            self.check_box_3_6.checked = False

    def check_box_3_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_3_6.checked is True:
            self.check_box_3_1.checked = False
            self.check_box_3_2.checked = False
            self.check_box_3_4.checked = False
            self.check_box_3_3.checked = False
            self.check_box_3_5.checked = False

    # ================================================================================= 4eme ligne
    def check_box_4_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_4_1.checked is True:
            self.check_box_4_2.checked = False
            self.check_box_4_3.checked = False
            self.check_box_4_4.checked = False
            self.check_box_4_5.checked = False
            self.check_box_4_6.checked = False

    def check_box_4_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_4_2.checked is True:
            self.check_box_4_1.checked = False
            self.check_box_4_3.checked = False
            self.check_box_4_4.checked = False
            self.check_box_4_5.checked = False
            self.check_box_4_6.checked = False

    def check_box_4_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_4_3.checked is True:
            self.check_box_4_1.checked = False
            self.check_box_4_2.checked = False
            self.check_box_4_4.checked = False
            self.check_box_4_5.checked = False
            self.check_box_4_6.checked = False

    def check_box_4_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_4_4.checked is True:
            self.check_box_4_1.checked = False
            self.check_box_4_3.checked = False
            self.check_box_4_2.checked = False
            self.check_box_4_5.checked = False
            self.check_box_4_6.checked = False

    def check_box_4_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_4_5.checked is True:
            self.check_box_4_1.checked = False
            self.check_box_4_2.checked = False
            self.check_box_4_4.checked = False
            self.check_box_4_3.checked = False
            self.check_box_4_6.checked = False

    def check_box_4_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_4_6.checked is True:
            self.check_box_4_1.checked = False
            self.check_box_4_2.checked = False
            self.check_box_4_4.checked = False
            self.check_box_4_3.checked = False
            self.check_box_4_5.checked = False

    # ================================================================================= 5eme ligne
    def check_box_5_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_5_1.checked is True:
            self.check_box_5_2.checked = False
            self.check_box_5_3.checked = False
            self.check_box_5_4.checked = False
            self.check_box_5_5.checked = False
            self.check_box_5_6.checked = False

    def check_box_5_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_5_2.checked is True:
            self.check_box_5_1.checked = False
            self.check_box_5_3.checked = False
            self.check_box_5_4.checked = False
            self.check_box_5_5.checked = False
            self.check_box_5_6.checked = False

    def check_box_5_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_5_3.checked is True:
            self.check_box_5_1.checked = False
            self.check_box_5_2.checked = False
            self.check_box_5_4.checked = False
            self.check_box_5_5.checked = False
            self.check_box_5_6.checked = False

    def check_box_5_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_5_4.checked is True:
            self.check_box_5_1.checked = False
            self.check_box_5_3.checked = False
            self.check_box_5_2.checked = False
            self.check_box_5_5.checked = False
            self.check_box_5_6.checked = False

    def check_box_5_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_5_5.checked is True:
            self.check_box_5_1.checked = False
            self.check_box_5_2.checked = False
            self.check_box_5_4.checked = False
            self.check_box_5_3.checked = False
            self.check_box_5_6.checked = False

    def check_box_5_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_5_6.checked is True:
            self.check_box_5_1.checked = False
            self.check_box_5_2.checked = False
            self.check_box_5_4.checked = False
            self.check_box_5_3.checked = False
            self.check_box_5_5.checked = False

    # ================================================================================= 6eme ligne
    def check_box_6_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_6_1.checked is True:
            self.check_box_6_2.checked = False
            self.check_box_6_3.checked = False
            self.check_box_6_4.checked = False
            self.check_box_6_5.checked = False
            self.check_box_6_6.checked = False

    def check_box_6_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_6_2.checked is True:
            self.check_box_6_1.checked = False
            self.check_box_6_3.checked = False
            self.check_box_6_4.checked = False
            self.check_box_6_5.checked = False
            self.check_box_6_6.checked = False

    def check_box_6_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_6_3.checked is True:
            self.check_box_6_1.checked = False
            self.check_box_6_2.checked = False
            self.check_box_6_4.checked = False
            self.check_box_6_5.checked = False
            self.check_box_6_6.checked = False

    def check_box_6_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_6_4.checked is True:
            self.check_box_6_1.checked = False
            self.check_box_6_3.checked = False
            self.check_box_6_2.checked = False
            self.check_box_6_5.checked = False
            self.check_box_6_6.checked = False

    def check_box_6_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_6_5.checked is True:
            self.check_box_6_1.checked = False
            self.check_box_6_2.checked = False
            self.check_box_6_4.checked = False
            self.check_box_6_3.checked = False
            self.check_box_6_6.checked = False

    def check_box_6_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_6_6.checked is True:
            self.check_box_6_1.checked = False
            self.check_box_6_2.checked = False
            self.check_box_6_4.checked = False
            self.check_box_6_3.checked = False
            self.check_box_6_5.checked = False

    # ================================================================================= 7eme ligne
    def check_box_7_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_7_1.checked is True:
            self.check_box_7_2.checked = False
            self.check_box_7_3.checked = False
            self.check_box_7_4.checked = False
            self.check_box_7_5.checked = False
            self.check_box_7_6.checked = False

    def check_box_7_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_7_2.checked is True:
            self.check_box_7_1.checked = False
            self.check_box_7_3.checked = False
            self.check_box_7_4.checked = False
            self.check_box_7_5.checked = False
            self.check_box_7_6.checked = False

    def check_box_7_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_7_3.checked is True:
            self.check_box_7_1.checked = False
            self.check_box_7_2.checked = False
            self.check_box_7_4.checked = False
            self.check_box_7_5.checked = False
            self.check_box_7_6.checked = False

    def check_box_7_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_7_4.checked is True:
            self.check_box_7_1.checked = False
            self.check_box_7_3.checked = False
            self.check_box_7_2.checked = False
            self.check_box_7_5.checked = False
            self.check_box_7_6.checked = False

    def check_box_7_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_7_5.checked is True:
            self.check_box_7_1.checked = False
            self.check_box_7_2.checked = False
            self.check_box_7_4.checked = False
            self.check_box_7_3.checked = False
            self.check_box_7_6.checked = False

    def check_box_7_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_7_6.checked is True:
            self.check_box_7_1.checked = False
            self.check_box_7_2.checked = False
            self.check_box_7_4.checked = False
            self.check_box_7_3.checked = False
            self.check_box_7_5.checked = False

    # ================================================================================= 8eme ligne
    def check_box_8_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_8_1.checked is True:
            self.check_box_8_2.checked = False
            self.check_box_8_3.checked = False
            self.check_box_8_4.checked = False
            self.check_box_8_5.checked = False
            self.check_box_8_6.checked = False

    def check_box_8_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_8_2.checked is True:
            self.check_box_8_1.checked = False
            self.check_box_8_3.checked = False
            self.check_box_8_4.checked = False
            self.check_box_8_5.checked = False
            self.check_box_8_6.checked = False

    def check_box_8_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_8_3.checked is True:
            self.check_box_8_1.checked = False
            self.check_box_8_2.checked = False
            self.check_box_8_4.checked = False
            self.check_box_8_5.checked = False
            self.check_box_8_6.checked = False

    def check_box_8_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_8_4.checked is True:
            self.check_box_8_1.checked = False
            self.check_box_8_3.checked = False
            self.check_box_8_2.checked = False
            self.check_box_8_5.checked = False
            self.check_box_8_6.checked = False

    def check_box_8_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_8_5.checked is True:
            self.check_box_8_1.checked = False
            self.check_box_8_2.checked = False
            self.check_box_8_4.checked = False
            self.check_box_8_3.checked = False
            self.check_box_8_6.checked = False

    def check_box_8_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_8_6.checked is True:
            self.check_box_8_1.checked = False
            self.check_box_8_2.checked = False
            self.check_box_8_4.checked = False
            self.check_box_8_3.checked = False
            self.check_box_8_5.checked = False

    # ================================================================================= 9eme ligne
    def check_box_9_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_9_1.checked is True:
            self.check_box_9_2.checked = False
            self.check_box_9_3.checked = False
            self.check_box_9_4.checked = False
            self.check_box_9_5.checked = False
            self.check_box_9_6.checked = False

    def check_box_9_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_9_2.checked is True:
            self.check_box_9_1.checked = False
            self.check_box_9_3.checked = False
            self.check_box_9_4.checked = False
            self.check_box_9_5.checked = False
            self.check_box_9_6.checked = False

    def check_box_9_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_9_3.checked is True:
            self.check_box_9_1.checked = False
            self.check_box_9_2.checked = False
            self.check_box_9_4.checked = False
            self.check_box_9_5.checked = False
            self.check_box_9_6.checked = False

    def check_box_9_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_9_4.checked is True:
            self.check_box_9_1.checked = False
            self.check_box_9_3.checked = False
            self.check_box_9_2.checked = False
            self.check_box_9_5.checked = False
            self.check_box_9_6.checked = False

    def check_box_9_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_9_5.checked is True:
            self.check_box_9_1.checked = False
            self.check_box_9_2.checked = False
            self.check_box_9_4.checked = False
            self.check_box_9_3.checked = False
            self.check_box_9_6.checked = False

    def check_box_9_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_9_6.checked is True:
            self.check_box_9_1.checked = False
            self.check_box_9_2.checked = False
            self.check_box_9_4.checked = False
            self.check_box_9_3.checked = False
            self.check_box_9_5.checked = False

    # ================================================================================= 10eme ligne
    def check_box_10_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_10_1.checked is True:
            self.check_box_10_2.checked = False
            self.check_box_10_3.checked = False
            self.check_box_10_4.checked = False
            self.check_box_10_5.checked = False
            self.check_box_10_6.checked = False

    def check_box_10_2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_10_2.checked is True:
            self.check_box_10_1.checked = False
            self.check_box_10_3.checked = False
            self.check_box_10_4.checked = False
            self.check_box_10_5.checked = False
            self.check_box_10_6.checked = False

    def check_box_10_3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_10_3.checked is True:
            self.check_box_10_1.checked = False
            self.check_box_10_2.checked = False
            self.check_box_10_4.checked = False
            self.check_box_10_5.checked = False
            self.check_box_10_6.checked = False

    def check_box_10_4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_10_4.checked is True:
            self.check_box_10_1.checked = False
            self.check_box_10_3.checked = False
            self.check_box_10_2.checked = False
            self.check_box_10_5.checked = False
            self.check_box_10_6.checked = False

    def check_box_10_5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_10_5.checked is True:
            self.check_box_10_1.checked = False
            self.check_box_10_2.checked = False
            self.check_box_10_4.checked = False
            self.check_box_10_3.checked = False
            self.check_box_10_6.checked = False

    def check_box_10_6_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_10_6.checked is True:
            self.check_box_10_1.checked = False
            self.check_box_10_2.checked = False
            self.check_box_10_4.checked = False
            self.check_box_10_3.checked = False
            self.check_box_10_5.checked = False

    # ================================================================
    def button_valider_click(self, **event_args):
        """This method is called when the button is clicked"""
        # check si une reponse par ligne
        nb = 0
        nb_ouv = 0
        nb_ouv_obligatoires = 0
        if (
            (self.check_box_1_1.checked is True)
            or (self.check_box_1_2.checked is True)
            or (self.check_box_1_3.checked is True)
            or (self.check_box_1_4.checked is True)
            or (self.check_box_1_5.checked is True)
            or (self.check_box_1_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_2_1.checked is True)
            or (self.check_box_2_2.checked is True)
            or (self.check_box_2_3.checked is True)
            or (self.check_box_2_4.checked is True)
            or (self.check_box_2_5.checked is True)
            or (self.check_box_2_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_3_1.checked is True)
            or (self.check_box_3_2.checked is True)
            or (self.check_box_3_3.checked is True)
            or (self.check_box_3_4.checked is True)
            or (self.check_box_3_5.checked is True)
            or (self.check_box_3_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_4_1.checked is True)
            or (self.check_box_4_2.checked is True)
            or (self.check_box_4_3.checked is True)
            or (self.check_box_4_4.checked is True)
            or (self.check_box_4_5.checked is True)
            or (self.check_box_4_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_5_1.checked is True)
            or (self.check_box_5_2.checked is True)
            or (self.check_box_5_3.checked is True)
            or (self.check_box_5_4.checked is True)
            or (self.check_box_5_5.checked is True)
            or (self.check_box_5_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_6_1.checked is True)
            or (self.check_box_6_2.checked is True)
            or (self.check_box_6_3.checked is True)
            or (self.check_box_6_4.checked is True)
            or (self.check_box_6_5.checked is True)
            or (self.check_box_6_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_7_1.checked is True)
            or (self.check_box_7_2.checked is True)
            or (self.check_box_7_3.checked is True)
            or (self.check_box_7_4.checked is True)
            or (self.check_box_7_5.checked is True)
            or (self.check_box_7_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_8_1.checked is True)
            or (self.check_box_8_2.checked is True)
            or (self.check_box_8_3.checked is True)
            or (self.check_box_8_4.checked is True)
            or (self.check_box_8_5.checked is True)
            or (self.check_box_8_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_9_1.checked is True)
            or (self.check_box_9_2.checked is True)
            or (self.check_box_9_3.checked is True)
            or (self.check_box_9_4.checked is True)
            or (self.check_box_9_5.checked is True)
            or (self.check_box_9_6.checked is True)
        ):
            nb += 1
        if (
            (self.check_box_10_1.checked is True)
            or (self.check_box_10_2.checked is True)
            or (self.check_box_10_3.checked is True)
            or (self.check_box_10_4.checked is True)
            or (self.check_box_10_5.checked is True)
            or (self.check_box_10_6.checked is True)
        ):
            nb += 1
        print("test nb questions fermées répondues: ", nb)
        global nb_questions_ferm
        print("test nb questions fermées dico: ", nb_questions_ferm)
        if nb != nb_questions_ferm:
            alert("Répondez à toutes les questions bleues svp !")
            return

        # tests si questions ouvertes obligatoires sont répondues
        global stage_row
        global dico_q_ferm
        global dico_q_ouv
        dico_ouv = dico_q_ouv

        if (
            self.column_panel_a1.visible is True and dico_ouv["1"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a1.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a2.visible is True and dico_ouv["2"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a2.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a3.visible is True and dico_ouv["3"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a3.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a4.visible is True and dico_ouv["4"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a4.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a5.visible is True and dico_ouv["5"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a5.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a6.visible is True and dico_ouv["6"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a6.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a7.visible is True and dico_ouv["7"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a7.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a8.visible is True and dico_ouv["8"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a8.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a9.visible is True and dico_ouv["9"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a9.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        if (
            self.column_panel_a10.visible is True and dico_ouv["10"][1] == "obligatoire"
        ):  # existe ds dico et obligatoire ?
            nb_ouv_obligatoires += 1  # cumul nb questions ouvertes obligatoires
            if self.text_area_a10.text != "":
                nb_ouv += 1  # Cumul nb questions ouvertes obligatoires répondues
        print("test nb questions ouvertes répondues: ", nb_ouv)

        global nb_questions_ouvertes
        print("test nb questions ouvertes dico: ", nb_questions_ouvertes)
        print("test nb questions ouvertes dico obligatoires: ", nb_ouv_obligatoires)
        if nb_ouv != nb_ouv_obligatoires:
            alert("Répondez à toutes les questions vertes obligatoires svp !")
            return

        """
                          CREATION DES DICT REPONSES
        """
        dico_rep_q_ferm = {}  #     clé:num question   valeur: = question txt,reponse (0 à 5)
        dico_rep_q_ouv = {}  #     clé:num question   valeur: = question txt,reponse (txt)
        # Questions fermées 
        for cp in self.get_components():  # column panels in form self
            if cp.tag != 0 and cp.tag != "header" and cp.tag != "q_ouvertes" and type(cp.tag) is int:  # si pas les col panel du haut de la forme, ce sont des cp des questions
                num_question = cp.tag
                if num_question <= nb_questions_ferm:
                    try:
                        for objet in cp.get_components():  # objets ds column panel
                            try:
                                if objet.tag == "label":
                                    question = objet.text
                                if objet.tag == "fp":
                                    cpt = 0
                                    rep = ""
                                    for box in objet.get_components():
                                        if box.checked is True:
                                            rep = cpt  # si rep1 est 2, indique 1
                                            clef = str(
                                                num_question
                                            )  # la clé doit être str qd j'envoie le dico en server-side
                                            valeur = (question, rep)
                                            dico_rep_q_ferm[clef] = valeur
                                            break
                                        else:
                                            cpt += 1
                                    print("question : ", num_question, "rep :", rep)
                            except:
                                pass
                    except:
                        pass
                else:  # nb de questions atteint, on sort
                    break

        # Création du dict réponses ouvertes
        clef = "1"  # num question ,  la clé doit être str qd j'envoie le dico en server-side
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a1.text, self.text_area_a1.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "2"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a2.text, self.text_area_a2.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "3"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a3.text, self.text_area_a3.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "4"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a4.text, self.text_area_a4.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "5"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a5.text, self.text_area_a5.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "6"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a6.text, self.text_area_a6.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "7"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a7.text, self.text_area_a7.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "8"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a8.text, self.text_area_a8.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "9"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a9.text, self.text_area_a9.text)
            dico_rep_q_ouv[clef] = valeur

        clef = "10"
        if int(clef) <= nb_questions_ouvertes:
            valeur = (self.label_a10.text, self.text_area_a10.text)
            dico_rep_q_ouv[clef] = valeur

        # Print pour vérif des 2 dicos
        print()
        print("============== Dict reponses fermées: ")
        print(dico_rep_q_ferm)
        print()
        print("============== Dict reponses ouvertes: ")
        print(dico_rep_q_ouv)

        date_time = ""
        date_time = French_zone.french_zone_time()  # importé en ht de ce script,
        print()
        date_time = str(date_time)[0:19]  # je prends les 19 1ers caract
        print(date_time)

        global stage_row
        global user_row
        # si user = stagiaire
        if user_row["role"]=="S":
            result = anvil.server.call("add_1_formulaire_suivi",
                                        user_row,    # user qui a rempli le formulaire
                                        stage_row,
                                        dico_rep_q_ferm,
                                        dico_rep_q_ouv,
                                        date_time,
                                        user_row["role"],  # Type du user qui a rempli le F:    S=stagiaire   T=Tuteur   F=Formateur
                                        stagiaire_du_tuteur=user_row["email"]      # le stagiaire qui est l'objet du formulaire 
                                    )
        else:   #user: Tuteur ou Formateur
            result = anvil.server.call("add_1_formulaire_suivi",
                                        user_row,    # user qui a rempli le formulaire
                                        stage_row,
                                        dico_rep_q_ferm,
                                        dico_rep_q_ouv,
                                        date_time,
                                        user_row["role"],  # Type du user qui a rempli le F:    S=stagiaire   T=Tuteur   F=Formateur
                                        #stagiaire_du_tuteur=self.row_stagiaire["email"]   #le stagiaire qui est l'objet du formulaire (si user est Tuteur ou Formateur) 
                                    )
        if result is True:
            if user_row["role"]=="T":
                alert("Merci pour vos réponses ! Formulaire sauvé.\n\n Si vous êtes Tuteur d'un autre stagiaire, remplissez un autre formulaire pour lui !\n\n SVP, RENTREZ VOTRE CARTE PRO !\n(Dans l'acceuil de cette application,\noption 'Documents à entrer')")
            else:
                alert("Merci pour vos réponses ! Formulaire sauvé.")
            self.button_annuler_click()
        else:
            alert("Le formulaire n'a pas été enregistré correctement !")

    def drop_down_stagiaires_change(self, **event_args):
        """This method is called when an item is selected"""
        global user_row
        self.row_stagiaire = self.drop_down_stagiaires.selected_value
        print("email du stagiaire choisi par le tuteur:",self.row_stagiaire["email"])
        self.text_area_a3.text = self.row_stagiaire["prenom"]+" "+self.row_stagiaire["nom"]

        # Recherche si un formulaire a déjà été rempli pour lui
        test = app_tables.stage_suivi.search(
            stage_row = self.drop_down_code_stage.selected_value,  # le stage sélectionné
            user_email = user_row["email"],                        #l'utilisateur du formulaire
            stagiaire_du_tuteur = self.row_stagiaire["email"]      #le stagiaire qui est l'objet du formulaire   
                                            )
        if len(test) >0:
            alert(f"Attention vous avez déjà rempli un rapport pour {self.text_area_a3.text} ! \n\n Vous pouvez toutefois remplir un nouveau rapport pour ce ou cette stagiaire.\n Tous les rapports seront conservés.")

    