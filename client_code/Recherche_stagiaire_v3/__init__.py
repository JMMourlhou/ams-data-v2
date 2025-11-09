from ._anvil_designer import Recherche_stagiaire_v3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from time import sleep
from ..Box_types_fi import Box_types_fi
from ..Box_stages import Box_stages


class Recherche_stagiaire_v3(Recherche_stagiaire_v3Template):
    def __init__(self, num_stage="", **properties):  # inscript="inscription" si vient de visu_stages pour inscription d'1 stagiare
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()  # form appelante
        self.user_now = anvil.users.get_user()
        # Affichage bouton effacement du stagiaire
        user = anvil.users.get_user()
        if user["role"] == "A" or user["role"]=="B": 
            self.button_del.visible = True
        # ==================================================================================   
        # Pour une inscription (self.num_stage != "") 
        self.label_origine.text = str(get_open_form())
        self.num_stage = num_stage
        self.label_num_stage.text = num_stage # sauvegarde du num de stage pour l'inscription
        if self.num_stage != "":
            self.drop_down_code_stage.visible = False
            self.drop_down_num_stages.visible = False
            self.button_add_to_stage.visible = True    # rend visible le bt + pour l'inscription
            # couleurs bt:
            #self.button_add_to_stage.foreground = "red"
            self.button_fiche.foreground = "yellow"
            self.button_qcm.foreground = "yellow"
            self.button_histo.foreground = "yellow"
            self.button_pr.foreground = "yellow"
            self.button_visu_formulaires.foreground = "yellow"
            self.button_mail.foreground = "yellow"
            self.button_del.foreground = "yellow"
        
        # drop_down mode fi pour le repeat_panel de Stage_visu_modif (si je clique sur l'historique, je vais visualiser le stage)
        # comme j'utilise le get_open_form() en stage_visu_modif, je dois insérer ici en recherche le drop down des modees de fi
        self.drop_down_mode_fi.items = [
            (r["code_fi"], r)
            for r in app_tables.mode_financement.search(
                tables.order_by("code_fi", ascending=True)
            )
        ]
        
        # Drop down codes stages
        self.drop_down_code_stage.items = [
            (r["code"], r)
            for r in app_tables.codes_stages.search(
                tables.order_by("code", ascending=True)
            )
        ]

        # ----------------------------------------------------------------------------------------------
        # import anvil.js    # pour screen size: Si tel: 3 data grid 3 rows sinon 8 pour ordinateur
        from anvil.js import window  # to gain access to the window objec
        screen_size = window.innerWidth
        #print("screen: ", screen_size)

        if screen_size >= 700:
            pass
            #self.data_grid_1.rows_per_page = 5
        else:  # Phone
            #self.data_grid_1.rows_per_page = 3
            self.button_mail_to_all.text = ""  # Affiche les icones uniqt
            self.button_trombi.text = ""
            self.button_pre_requis.text = ""
    
    # Focus on nom en ouverture de form
    def form_show(self, **event_args):
        self.text_box_nom.focus()
    
    def filtre_type_stage(self):
        # Récupération du critère stage
        row_type = self.drop_down_code_stage.selected_value
        # lecture du fichier stages et sélection des stages correspond au type de stage choisit
        list1 = app_tables.stages.search(
            q.fetch_only("date_debut", "numero"),  # recherche ds les stages
            tables.order_by("date_debut", ascending=False),
            code=row_type,
        )
        if len(list1) == 0:
            open_form("Recherche_stagiaire_v3")

        # Initialisation du Drop down num_stages et dates
        self.drop_down_num_stages.items = [
            (str(r["date_debut"]) + " / " + str(r["numero"]), r) for r in list1
        ]

        """
        for r in self.drop_down_num_stages.items:           # Je peux boucler ds ma dropdown
            print(r, r[0], r[1])                            # je peux extraire 0 ce qui est affiché, 1 row stage
        """

        # affichage de tous les stagiaires de ces stages du type choisit
        liste_intermediaire1 = []
        for st in list1:  # boucle sur les stages de même type (ex psc1)
            # date = st["date_debut"]    #DATE DU STAGE
            # lecture du fichier stagiaires_inscrits sur le stage et création d'1 liste par stage
            temp = app_tables.stagiaires_inscrits.search(
                q.fetch_only(), tables.order_by("name", ascending=True), stage=st
            )
            liste_intermediaire1.append(temp)  # ajout de la liste (iterator object)du stage

        # print("nb de listes créées: ",len(liste_intermediaire1))

        # Je crée 1 liste à partir de ttes les listes créées:
        self.liste_type_stage = []
        for l in liste_intermediaire1:  # pour chaque liste iterator object
            for row in l:  # pour chaque stagiaire du stage
                self.liste_type_stage.append(row)
        self.label_titre.text = str(len(self.liste_type_stage)) + " résultats"

        self.data_grid_users.visible = False
        self.repeating_panel_0.visible = True
        self.data_grid_users.visible = True
        self.repeating_panel_0.items = self.liste_type_stage
        if len(self.liste_type_stage) > 0:
            self.button_mail_to_all.visible = True
            self.drop_down_num_stages.visible = True
            self.button_trombi.visible = True

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        self.text_box_nom.text = ""  # critere nom
        self.text_box_prenom.text = ""  # critere prenom
        self.text_box_email.text = ""  # critere email
        self.text_box_tel.text = ""  # critere tel
        self.drop_down_num_stages.visible = False
        #self.column_panel_search.visible = False
        self.raz_screen()
        self.filtre_type_stage()

    def drop_down_num_stages_change(self, **event_args):
        """This method is called when an item is selected"""
        self.selection = self.drop_down_num_stages.selected_value
        # extraction du num stage
        self.liste_date = app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True), stage=self.selection
        )
        self.label_titre.text = str(len(self.liste_date)) + " résultats"
        self.button_insc_par_qr.visible = True  # Affiche BT inscription par QR
        self.repeating_panel_0.items = self.liste_date
        if len(self.liste_date) > 0:  # Stagiaires inscrits
            self.button_mail_to_all.visible = True
            self.button_trombi.visible = True
            self.button_pre_requis.visible = True
        else:  # Pas de stagiaires inscrits
            self.button_mail_to_all.visible = False
            self.button_mail_to_all.visible = False
            # self.button_trombi.visible = False
            self.button_pre_requis.visible = False

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        # from ..Main import Main
        # open_form('Main',99)
        open_form(self.f)

    def button_efface_click(self, **event_args):  # # j'efface les critères
        """This method is called when the button is clicked"""
        open_form("Recherche_stagiaire_v3", self.num_stage)

    def text_box_nom_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_recherche_click()

    def text_box_role_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_recherche_click()

    def text_box_prenom_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_recherche_click()

    def text_box_tel_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_recherche_click()

    def text_box_email_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_recherche_click()

    def button_mail_to_all_click(self, **event_args):
        """This method is called when the button is clicked"""
        if (
            self.drop_down_num_stages.selected_value is not None
        ):  # si drop down date sélectionnée
            liste = self.liste_date
        else:
            liste = (
                self.liste_type_stage
            )  # sinon je prends la liste par type de stage (PSE1, PSE2...)

        liste_email = []
        for stagiaire in liste:
            liste_email.append(
                (stagiaire["user_email"]["email"], stagiaire["prenom"], "")
            )  # 3 infos given, "" indique qu'il ny a pas d'id (cas des olds stgiaires)

        # 'formul' indique l'origine, ici 'formulaire de satisfaction'
        open_form("Mail_subject_attach_txt", liste_email, "stagiaire_tous")

    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_trombi import Visu_trombi

        if self.drop_down_num_stages.selected_value is not None:  # 1 stage sélectionné
            open_form(
                "Visu_trombi",
                str(self.selection["numero"]),
                self.selection["code"]["intitulé"],
                False,
                None,
                False,
            )
        else:
            code_stage = self.drop_down_code_stage.selected_value["code"]
            open_form("Visu_trombi", None, None, True, code_stage, False)

    def button_pre_requis_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form("Pre_R_pour_stagiaire_admin", self.selection["numero"])

    def button_insc_par_qr_click(self, **event_args):
        """This method is called when the button is clicked"""
        # si True, appel du qr_code pour que les stagiaires log in ds l'appli
        open_form("QrCode_display", False, str(self.selection["numero"]))

    def text_box_nom_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_prenom.text = ""
        self.text_box_email.text = ""
        self.text_box_tel.text = ""

        critere = self.text_box_nom.text + "%"  #  wildcard search on date
        liste = app_tables.users.search(
            tables.order_by("nom", ascending=True),
            q.fetch_only("role", "nom", "prenom", "tel", "email"),
            nom=q.ilike(critere),
        )
        self.raz_screen()
        self.label_titre.text = str(len(liste)) + " résultats"
        self.repeating_panel_0.items = liste
        self.drop_down_code_stage.selected_value = None
        self.drop_down_num_stages.selected_value = None
        
    def text_box_prenom_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_email.text = ""
        self.text_box_tel.text = ""

        critere = self.text_box_prenom.text + "%"  #  wildcard search on prenom
        liste = app_tables.users.search(
            tables.order_by("prenom", ascending=True),
            q.fetch_only("role", "nom", "prenom", "tel", "email"),
            prenom=q.ilike(critere),
        )
        self.raz_screen()
        self.label_titre.text = str(len(liste)) + " résultats"
        self.repeating_panel_0.items = liste
        self.drop_down_code_stage.selected_value = None
        self.drop_down_num_stages.selected_value = None

        

    def text_box_role_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_email.text = ""
        self.text_box_tel.text = ""

        # Initialisation de l'affichage par role
        critere = self.text_box_role.text + "%"  #  wildcard search on role
        liste = app_tables.users.search(
            tables.order_by("role", ascending=True),
            q.fetch_only("role", "nom", "prenom", "tel", "email"),
            role=q.ilike(critere),
        )
        self.raz_screen()
        self.label_titre.text = str(len(liste)) + " résultats"
        self.repeating_panel_0.items = liste
        self.drop_down_code_stage.selected_value = None
        self.drop_down_num_stages.selected_value = None
        
        

    def text_box_email_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_tel.text = ""

        critere = self.text_box_email.text + "%"  #  wildcard search on email
        liste = app_tables.users.search(
            tables.order_by("email", ascending=True),
            q.fetch_only("role", "nom", "prenom", "tel", "email"),
            email=q.ilike(critere),
        )
        self.raz_screen()
        self.label_titre.text = str(len(liste)) + " résultats"
        self.repeating_panel_0.items = liste
        self.drop_down_code_stage.selected_value = None
        self.drop_down_num_stages.selected_value = None

        

    def text_box_tel_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_email.text = ""

        critere = self.text_box_tel.text + "%"  #  wildcard search on tel
        liste = app_tables.users.search(
            tables.order_by("tel", ascending=True),
            q.fetch_only("role", "nom", "prenom", "tel", "email"),
            tel=q.ilike(critere),
        )
        self.raz_screen()
        self.label_titre.text = str(len(liste)) + " résultats"
        self.repeating_panel_0.items = liste
        self.drop_down_code_stage.selected_value = None
        self.drop_down_num_stages.selected_value = None

        

    def raz_screen(self):   
        self.data_grid_users.visible = True
        self.repeating_panel_histo.visible = False
        self.repeating_panel_pr.visible = False
        self.repeating_panel_qcm.visible = False
        
        self.column_panel_formulaires_fin.visible = False # formulares de fin
        self.column_panel_formulaires_suivis.visible = False # Formulaires de suivi
        self.repeating_panel_formulaires_fin.items = []
        self.repeating_panel_formulaires_suivis.items = []

        self.repeating_panel_formul_fin_questions_fermees.visible = False
        self.repeating_panel_formul_fin_questions_ouvertes.visible = False
        self.repeating_panel_formul_suivi_questions_ouvertes.visible = False
        self.repeating_panel_formul_suivi_questions_fermees.visible = False
        self.repeating_panel_formul_fin_questions_fermees.items = []
        self.repeating_panel_formul_fin_questions_ouvertes.items = []
        self.repeating_panel_formul_suivi_questions_ouvertes.items = []
        self.repeating_panel_formul_suivi_questions_fermees.items = []
        
        
        self.column_panel_stagiaire.visible = False
        self.column_panel_menu.visible = False
        
        self.button_mail_to_all.visible = False
        self.button_trombi.visible = False
        self.button_pre_requis.visible = False
        self.button_insc_par_qr.visible = False
        
        self.button_role.text = ""
        self.button_nom_p.text = ""
        #self.button_3.text = ""
        self.button_tel.text = ""
        
    def button_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_histo.visible = False
        self.repeating_panel_pr.visible = False
        self.column_panel_formulaires_fin.visible = False
        
            
        # lecture du user sur le mail sauvé en label_user_email
        try:
            self.item = app_tables.users.get(email=self.label_user_email.text)
        except Exception as e:
            alert(f"Erreur en re-lecture du user: {e}")
    
        qcm_results = app_tables.qcm_result.search( 
            tables.order_by("time", ascending=False),
            user_qcm = self.item
        )
        if len(qcm_results)>0:      # qcm trouvés pour ce user
            # self.repeating_panel_qcm.visible = True
            self.repeating_panel_qcm.items = qcm_results
            self.data_grid_users.visible = False
            
            # j'affiche si les résultats n'étaient pas déjà visible
            if self.repeating_panel_qcm.visible is False:
                self.repeating_panel_qcm.visible = True
                # couleurs bt:
                self.button_qcm.foreground = "red"
                self.button_nom_p.foreground = "red"
                self.button_fiche.foreground = "yellow"
                self.button_histo.foreground = "yellow"
                self.button_pr.foreground = "yellow"
                self.button_visu_formulaires.foreground = "yellow"
                self.button_mail.foreground = "yellow"
                self.button_del.foreground = "yellow"
                self.button_add_to_stage.foreground = "yellow"
            else:
                self.repeating_panel_qcm.visible = False
                self.button_qcm.foreground = "yellow"
        else:
            self.repeating_panel_qcm.visible = False
            self.button_qcm.foreground = "yellow"


    def button_histo_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_qcm.visible = False
        self.repeating_panel_pr.visible = False
        self.column_panel_formulaires_fin.visible = False
        # lecture du user sur le mail sauvé en label_user_email
        try:
            self.item = app_tables.users.get(email=self.label_user_email.text)
        except Exception as e:
            alert(f"Erreur en re-lecture du user: {e}")

        # lecture de l'historique en table stgiaire inscrit
        list =  app_tables.stagiaires_inscrits.search(
            tables.order_by("numero", ascending=False),
            user_email = self.item
        )
        if len(list) == 0:
            self.button_histo.foreground = "yellow"
            self.repeating_panel_histo.visible = False
        else:                      
            #self.repeating_panel_histo.visible = True
            self.repeating_panel_histo.items = list 
            
            # j'affiche si les résultats n'étaient pas déjà visible
            if self.repeating_panel_histo.visible is False:
                self.repeating_panel_histo.visible = True
                # couleurs bt:
                self.button_histo.foreground = "red"
                self.button_nom_p.foreground = "red"
                self.button_fiche.foreground = "yellow"
                self.button_qcm.foreground = "yellow"
                self.button_pr.foreground = "yellow"
                self.button_visu_formulaires.foreground = "yellow"
                self.button_mail.foreground = "yellow"
                self.button_del.foreground = "yellow"
                self.button_add_to_stage.foreground = "yellow"
                self.data_grid_users.visible = False
            else:
                self.repeating_panel_histo.visible = False
                self.button_histo.foreground = "yellow"
            
        

    def button_pr_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_histo.visible = False
        self.repeating_panel_qcm.visible = False
        self.column_panel_formulaires_fin.visible = False
        # lecture du user sur le mail sauvé en label_user_email
        try:
            self.item = app_tables.users.get(email=self.label_user_email.text)
        except Exception as e:
            alert(f"Erreur en re-lecture du user: {e}")
            
        # Acquisition des stages où le stagiaire est inscrit
        liste0 = app_tables.stagiaires_inscrits.search( q.fetch_only("stage_txt"),
                                                            user_email=self.item)

        if liste0 is None:
            return
        if self.repeating_panel_pr.visible is False:
            self.repeating_panel_pr.visible = True
            # couleurs bt:
            self.button_pr.foreground = "red"
            self.button_nom_p.foreground = "red"
            self.button_fiche.foreground = "yellow"
            self.button_qcm.foreground = "yellow"
            self.button_histo.foreground = "yellow"
            self.button_visu_formulaires.foreground = "yellow"
            self.button_mail.foreground = "yellow"
            self.button_del.foreground = "yellow"
            self.button_add_to_stage.foreground = "yellow"
        else:
            self.repeating_panel_pr.visible = False
            self.button_pr.foreground = "yellow"

        # pour chaque stage, je lis les pré requis en table pré requis stagiaires
        # Création du dict des pr du stagiaire
        self.dico_pre_requis = {}
        for stage in liste0:
            liste_pr = app_tables.pre_requis_stagiaire.search(stagiaire_email=stage['user_email'],
                                                                numero=stage['numero']
                                                                )
            # création du dico des pré-requis 
            # print(liste_pr[0])

            for pr in liste_pr:
                valeur = None
                clef = pr['requis_txt']
                valeur = (pr['stage_num'], pr['item_requis'], pr['code_txt'], pr['stagiaire_email'], pr['doc1'])
                # Si la clé n'existe pas encore, ou si la valeur actuelle est None et la nouvelle non None
                if clef not in self.dico_pre_requis  or  (self.dico_pre_requis[clef][1] is None and pr['doc1'] is not None):
                    self.dico_pre_requis[clef] = valeur

        # Fin de boucle le dico contient le résumé de tous les pr du stagiare et True si présent        
        """
        for clef in self.dico_pre_requis:
            print (clef,self.dico_pre_requis[clef])
        """
        # Transformation en liste
        # -----------------------------------------------------------
        # Transformation en liste pour affichage dans le RepeatingPanel
        liste_affichage = []

        for clef, (numero, requis_row, type_stage_txt ,email, doc1) in self.dico_pre_requis.items():
            liste_affichage.append({
                "requis_txt": clef,
                "item_requis": requis_row,
                "type_stage_txt": type_stage_txt,
                "stagiaire_email": email,
                "stage_num": numero,
                "doc1": doc1
            })

        # Affectation au RepeatingPanel pour affichage
        if liste_affichage != []:
            self.repeating_panel_pr.items = liste_affichage
        else:
            self.repeating_panel_pr.visible = False
            self.button_pr.foreground = "yellow"
            #self.user_initial_color()

    def button_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        # lecture du user sur le mail sauvé en label_user_email
        try:
            self.item = app_tables.users.get(email=self.label_user_email.text)
        except Exception as e:
            alert(f"Erreur en re-lecture du user: {e}")
            
        # couleurs bt:
        self.button_mail.foreground = "red"
        self.button_nom_p.foreground = "red"
        self.button_fiche.foreground = "yellow"
        self.button_qcm.foreground = "yellow"
        self.button_histo.foreground = "yellow"    
        self.button_visu_formulaires.foreground = "yellow"   
        self.button_del.foreground = "yellow"
        self.button_add_to_stage.foreground = "yellow"
        
        liste_email = []
        liste_email.append((self.item['email'],self.item['prenom'],""))   # mail et prénom, id pas besoin
        open_form('Mail_subject_attach_txt',liste_email,"stagiaire_1")

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Effacement du stagiaire/formateur si pas ds un stage et si je suis l'administrateur
        user = anvil.users.get_user()
        if user["role"] == "A" or user["role"]=="B":   # seul,l'administrateur et bureaux peuvent effacer definitivement un stagiaire ou formateur ou tuteur
            # Cette personne est-elle inscrite ds un ou plusieurs stages ?
            # lecture du user sur le mail sauvé en label_user_email
            try:
                self.item = app_tables.users.get(email=self.label_user_email.text)
            except Exception as e:
                alert(f"Erreur en re-lecture du user: {e}")
            list = app_tables.stagiaires_inscrits.search(user_email=self.item)
            detail =""
            for stage in list:
                detail=detail+str(stage['numero'])+"  "

            nb_stages = len(list)
            if nb_stages != 0:
                txt="stage"
                if nb_stages > 1:
                    txt = "stages"
                alert(f"Effacement impossible:\nCette personne est inscrite dans {nb_stages} {txt}\n\n Détail:\n{txt} N°{detail}")
                self.button_histo_click()   # visu de l'histo du stagiaire
                return
            # Effact de la personne si confirmation
            # couleurs bt:
            self.button_del.foreground = "red"
            self.button_nom_p.foreground = "red"
            self.button_fiche.foreground = "yellow"
            self.button_qcm.foreground = "yellow"
            self.button_histo.foreground = "yellow"
            self.button_pr.foreground = "yellow"
            self.button_visu_formulaires.foreground = "yellow"
            self.button_mail.foreground = "yellow"
            self.button_add_to_stage.foreground = "yellow"
            r=alert("Voulez-vous vraiment enlever définitivement cette personne ? ",dismissible=False ,buttons=[("oui",True),("non",False)])
            if r :   # oui
                # lecture row users
                row = app_tables.users.get(email=self.item['email'])
                if row:
                    txt_msg = anvil.server.call("del_personne",row)
                alert(txt_msg)
            open_form("Recherche_stagiaire_v3")
            
    def button_fiche_click(self, **event_args):
        """This method is called when the button is clicked"""
        print("Mode inscription si stage pas vide: ",self.label_origine.text, self.label_num_stage.text)
        if self.label_origine.text == "<AMS_Data.Main.Main object>" or self.label_num_stage.text == "":    # vient du menu / recherche, pas d'inscription // 
            # lecture du user sur le mail sauvé en label_user_email
            try:
                self.item = app_tables.users.get(email=self.label_user_email.text)
            except Exception as e:
                alert(f"Erreur en re-lecture du user: {e}")
            # couleurs bt:
            self.button_fiche.foreground="red"
            self.button_qcm.foreground = "yellow"
            self.button_histo.foreground = "yellow"
            self.button_pr.foreground = "yellow"
            self.button_visu_formulaires.foreground = "yellow"
            self.button_mail.foreground = "yellow"
            self.button_del.foreground = "yellow"
            self.button_add_to_stage.foreground = "yellow"
            
            self.text_box_nom.text = self.item['nom']
            from ..Saisie_info_apres_visu import Saisie_info_apres_visu    
            if self.item['role'] == "A" and  self.user_now['role'] == "A": # Seul l'admin voit la fiche de l'admin
                open_form('Saisie_info_apres_visu', self.item['email'], num_stage=0, intitule="")
            if self.item['role'] != "A":
                open_form('Saisie_info_apres_visu', self.item['email'], num_stage=0, intitule="")

    def button_add_to_stage_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        # self.c.label_num_stage.text   est en forme mère recherche_stagiaire
        try:
            stagiaire_row = app_tables.users.get(email=self.label_user_email.text)
        except Exception as e:
            alert(f"Erreur en re-lecture du user: {e}")
        
        stage = self.label_num_stage.text
        print(f"stage en inscription: <{stage}>")

        self.content_panel.visible = True
        if int(stage) != 1003:   # tous stages sauf tuteurs
            self.content_panel.add_component(Box_types_fi(stagiaire_row, stage), full_width_row=False)
        else:  # Ajout d'un Tuteur   
            self.content_panel.add_component(Box_stages(stagiaire_row, stage), full_width_row=False)
        self.content_panel.scroll_into_view()

    def button_visu_formulaires_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_histo.visible = False
        self.repeating_panel_qcm.visible = False
        self.repeating_panel_pr.visible = False
        
        # lecture du user sur le mail sauvé en label_user_email
        try:
            self.item = app_tables.users.get(email=self.label_user_email.text)
        except Exception as e:
            alert(f"Erreur en re-lecture du user: {e}")

        # ==================================  Formulaires de FIN de stage
        list_formulaires_fin=[]
        list_formulaires_fin = app_tables.stage_satisf.search(user_email=self.item)
        if len(list_formulaires_fin)==0:
            self.column_panel_formulaires_fin.visible  = False
            self.button_visu_formulaires.foreground = "yellow"
        else:
            self.repeating_panel_formulaires_fin.items = list_formulaires_fin
            # affichage si pas déjà affiché
            if self.column_panel_formulaires_fin.visible is False:
                    self.column_panel_formulaires_fin.visible = True
                    self.data_grid_users.visible = False
                    # couleurs bt:
                    self.button_visu_formulaires.foreground = "red"
                    self.button_nom_p.foreground = "red"
                    self.button_fiche.foreground = "yellow"
                    self.button_qcm.foreground = "yellow"
                    self.button_pr.foreground = "yellow"
            else:
                self.button_visu_formulaires.foreground = "yellow"
                self.column_panel_formulaires_fin.visible = False
                
        # ==================================  Formulaires de SUIVIS de stage
        list_formulaires_suivis=[]
        list_formulaires_suivis = app_tables.stage_suivi.search(user_email=self.item['email'])
        if len(list_formulaires_suivis)==0:
            self.column_panel_formulaires_suivis.visible  = False
            self.button_visu_formulaires.foreground = "yellow"
        else:
            self.repeating_panel_formulaires_suivis.items = list_formulaires_suivis
            # affichage si pas déjà affiché
            if self.column_panel_formulaires_suivis.visible is False:
                self.column_panel_formulaires_suivis.visible = True
                self.data_grid_users.visible = False
                # couleurs bt:
                self.button_visu_formulaires.foreground = "red"
                self.button_nom_p.foreground = "red"
                self.button_fiche.foreground = "yellow"
                self.button_qcm.foreground = "yellow"
                self.button_pr.foreground = "yellow"
            else:
                self.button_visu_formulaires.foreground = "yellow"
                self.column_panel_formulaires_suivis.visible = False

   
    




    
        


    
   

    
        