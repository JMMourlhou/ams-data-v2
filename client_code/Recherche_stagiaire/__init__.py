from ._anvil_designer import Recherche_stagiaireTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Recherche_stagiaire(Recherche_stagiaireTemplate):
    def __init__(self, num_stage="", **properties):       # inscript="inscription" si vient de visu_stages pour inscription d'1 stagiare
         
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
            
        # Pour une inscription (self.num_stage != "")
        self.label_origine.text = str(get_open_form())
        self.num_stage = num_stage
        self.label_num_stage.text = num_stage
        if self.num_stage != "":  
            self.drop_down_code_stage.visible = False
            self.drop_down_num_stages.visible = False

        # drop_down mode fi pour le repeat_panel de Stage_visu_modif (si je clique sur l'historique, je vais visualise le stage)
        # comme j'utilise le get_open_form() en stage_visu_modif, je dois insérer ici en recherche le drop down des modees de fi
        self.drop_down_mode_fi.items = [(r['code_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("code_fi", ascending=True))]
        
        # Drop down codes stages
        self.drop_down_code_stage.items = [(r['code'], r) for r in app_tables.codes_stages.search(tables.order_by("code", ascending=True))]

        #import anvil.js    # pour screen size: Si tel: 3 data grid 3 rows sinon 8 pour ordinateur
        from anvil.js import window # to gain access to the window objec
        screen_size = window.innerWidth
        print("screen: ", screen_size)
        if screen_size > 700:
            self.data_grid_1.rows_per_page = 6
        else: # Phone
            self.button_mail_to_all.text = ""  # Affiche les icones uniqt
            self.button_trombi.text = ""
            self.button_pre_requis.text = ""
        if screen_size > 1800:
            self.data_grid_1.rows_per_page = 11
            
    # Focus on nom en ouverture de form
    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.text_box_nom.focus()
        
    def filtre(self):
        liste = []
        # Récupération des critères
        c_role = self.text_box_role.text + "%"          #  wildcard, critère role
        c_nom = self.text_box_nom.text + "%"            #            nom
        c_prenom = self.text_box_prenom.text + "%"      #            prenom
        c_email = self.text_box_email.text + "%"        #            email
        c_tel = self.text_box_tel.text + "%"            #            tel

        from ..import French_zone
        start = French_zone.french_zone_time()
        # Nom    
        if self.text_box_nom.text != "" and self.text_box_email.text == "" and self.text_box_tel.text == "" and self.text_box_prenom.text == "" and self.text_box_role.text == "" :
            #liste = anvil.server.call("search_on_name_only", c_nom)
            
            liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        nom    = q.ilike(c_nom),    # ET
                                    )
            
            end = French_zone.french_zone_time()
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ tps écoulé", end-start)
        # Prénom
        if self.text_box_prenom.text != "" and self.text_box_email.text == "" and self.text_box_tel.text == "" and self.text_box_nom.text == "" and self.text_box_role.text == "":   
            liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                       
                                        prenom    = q.ilike(c_prenom),    # ET
                                    )
        # Role
        if self.text_box_role.text != "" and self.text_box_nom.text == "" and self.text_box_prenom.text == "" :   
            liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                            role   = q.ilike(c_role)
                                    )
        # Role & Nom
        if self.text_box_role.text != "" and self.text_box_nom.text != "" and self.text_box_prenom.text == "" :   
            #liste = anvil.server.call("search_on_role_nom", c_role, c_nom)
            liste = app_tables.users.search(    q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        q.all_of                  # all of queries must match
                                        (
                                            role   = q.ilike(c_role),   # ET
                                            nom    = q.ilike(c_nom)   
                                        )
                                    )
        # Nom & Prénom
        if self.text_box_role.text == "" and self.text_box_nom.text != "" and self.text_box_prenom.text != "" :   
            #liste = anvil.server.call("search_on_nom_prenom", c_nom, c_prenom)        
            liste = app_tables.users.search(    q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        q.all_of                  # all of queries must match
                                        (
                                            prenom   = q.ilike(c_prenom),   # ET
                                            nom    = q.ilike(c_nom)   
                                        )
                                    )
            
        # Role & Nom & Prénom
        if self.text_box_role.text != "" and self.text_box_nom.text != "" and self.text_box_prenom.text != "" :   
            #liste = anvil.server.call("search_on_role_nom_prenom", c_role, c_nom, c_prenom)        
            liste = app_tables.users.search(    q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        q.all_of                  # all of queries must match
                                        (
                                            role   = q.ilike(c_role),   # ET
                                            prenom   = q.ilike(c_prenom),   # ET
                                            nom    = q.ilike(c_nom)   
                                        )
                                    )
        # Tel
        if self.text_box_tel.text != "" and self.text_box_email.text == "" and self.text_box_nom.text == "" and self.text_box_prenom.text == "" and self.text_box_role.text == "" :  
            #liste = anvil.server.call("search_on_tel_only", c_tel)
            liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("tel", ascending=True),
                                        tel   = q.ilike(c_tel)
                                    )
        # Mail
        if self.text_box_email.text != "" and self.text_box_tel.text == "" and self.text_box_nom.text == "" and self.text_box_prenom.text == "" and self.text_box_role.text == "" :  
            #liste = anvil.server.call("search_on_email_only", c_email)
            liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("email", ascending=True),
                                        email   = q.ilike(c_email)
                                    )
        self.label_titre.text = str(len(liste))+" résultats"
        self.repeating_panel_1.items = liste

    
    def filtre_type_stage(self):
        # Récupération du critère stage
        row_type = self.drop_down_code_stage.selected_value

        #lecture du fichier stages et sélection des stages correspond au type de stage choisit
        list1 = app_tables.stages.search(q.fetch_only("date_debut", "numero"),       # recherche ds les stages
                                            code=row_type)                        
        if len(list1)==0:
            from anvil import open_form       # j'initialise la forme principale avec le choix du qcm ds la dropdown
            open_form("Recherche_stagiaire") 
            
        # Initialisation du Drop down num_stages et dates
        self.drop_down_num_stages.items = [(str(r['date_debut'])+" / "+str(r['numero']), r) for r in list1]
        
        """
        for r in self.drop_down_num_stages.items:           # Je peux boucler ds ma dropdown
            print(r, r[0], r[1])                            # je peux extraire 0 ce qui est affiché, 1 row stage
        """    
        
        #affichage de tous les stagiaires de ces stages du type choisit
        liste_intermediaire1=[]
        for st in list1:               # boucle sur les stages de même type (ex psc1)                
            #date = st["date_debut"]    #DATE DU STAGE
            # lecture du fichier stagiaires_inscrits sur le stage et création d'1 liste par stage
            temp =  app_tables.stagiaires_inscrits.search(  q.fetch_only(),
                                                            tables.order_by("name", ascending=True),
                                                            stage=st
                                                         )
            liste_intermediaire1.append(temp)   # ajout de la liste (iterator object)du stage
            
        #print("nb de listes créées: ",len(liste_intermediaire1))
        
        # Je crée 1 liste à partir de ttes les listes créées:
        self.liste_type_stage = []
        for l in liste_intermediaire1:    #pour chaque liste iterator object
            for row in l:                      # pour chaque stagiaire du stage
                self.liste_type_stage.append(row)
        self.label_titre.text = str(len(self.liste_type_stage))+" résultats"
       
        self.repeating_panel_1.items = self.liste_type_stage
        if len(self.liste_type_stage)>0:
            self.button_mail_to_all.visible = True
            self.drop_down_num_stages.visible = True
    
    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        self.text_box_nom.text=""       # critere nom
        self.text_box_prenom.text=""  # critere prenom
        self.text_box_email.text=""  # critere email
        self.text_box_tel.text=""  # critere tel
        self.drop_down_num_stages.visible = False
        self.button_recherche.visible = False
        self.button_efface.visible = True
        self.column_panel_users.visible = False
        self.filtre_type_stage()  
        
    def drop_down_num_stages_change(self, **event_args):
        """This method is called when an item is selected"""
        self.selection=self.drop_down_num_stages.selected_value
        #extraction du num stage
        self.liste_date = app_tables.stagiaires_inscrits.search(
                                        tables.order_by("name", ascending=True),
                                        stage=self.selection
                                      )
        self.label_titre.text = str(len(self.liste_date))+" résultats"
        self.button_insc_par_qr.visible = True    # Affiche BT inscription par QR
        self.repeating_panel_1.items = self.liste_date
        if len(self.liste_date)>0:                     # Stagiaires inscrits
            self.button_mail_to_all.visible = True
            self.button_trombi.visible = True
            self.button_pre_requis.visible = True
        else:                                           # Pas de stagiaires inscrits
            self.button_mail_to_all.visible = False
            self.button_mail_to_all.visible = False
            self.button_trombi.visible = False
            self.button_pre_requis.visible = False

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def button_recherche_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.drop_down_code_stage.selected_value = None
        self.drop_down_num_stages.visible = False
        self.button_recherche.visible = False
        self.button_efface.visible = True
        self.column_panel_users.visible = False
        self.filtre()

    def button_efface_click(self, **event_args):    # # j'efface les critères
        """This method is called when the button is clicked"""
        open_form('Recherche_stagiaire', self.num_stage)

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

    def text_box_role_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_recherche.visible = True

    def button_mail_to_all_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.drop_down_num_stages.selected_value != None:    # si drop down date sélectionnée
            liste = self.liste_date
        else:
            liste = self.liste_type_stage   # sinon je prends la liste par type de stage (PSE1, PSE2...)
            
        
        liste_email = []
        for stagiaire in liste:
            liste_email.append((stagiaire["user_email"]["email"], stagiaire["prenom"], ""))   # 3 infos given, "" indique qu'il ny a pas d'id (cas des olds stgiaires)
        
        # 'formul' indique l'origine, ici 'formulaire de satisfaction'
        open_form("Mail_subject_attach_txt",  liste_email, 'stagiaire_tous') 

    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_trombi import Visu_trombi
        #open_form('Visu_trombi',self.text_box_num_stage.text, self.text_box_intitule.text, False)
        open_form('Visu_trombi',str(self.selection['numero']), self.selection['code']['intitulé'], False)

    def button_pre_requis_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('Pre_R_pour_stagiaire_admin',self.selection['numero'])

    def button_insc_par_qr_click(self, **event_args):
        """This method is called when the button is clicked"""
        # si True, appel du qr_code pour que les stagiaires log in ds l'appli
        open_form('QrCode_display',False, str(self.selection['numero']))


