from ._anvil_designer import MainTemplate
from anvil import *
import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

from .. import French_zone
from ..Saisie_info_de_base import Saisie_info_de_base
from ..Stage_creation import Stage_creation
from ..Visu_stages.RowTemplate3 import RowTemplate3
from anvil import open_form


#-------------------------------------------------------------------
# Pour mettre au format Francais les calendriers
from anvil.js.window import moment, document
script = document.createElement('script')
script.src = "https://cdn.jsdelivr.net/npm/moment@2.29.1/locale/fr.js" 
document.head.appendChild(script)
locale = moment.locale('fr')
# this doesn't happen instantly so set it and then wait
while locale != 'fr':
    from time import sleep
    sleep(.01)
    locale = moment.locale()
#---------------------------------------------------------------------


class Main(MainTemplate):
    def __init__(self, nb=1, stage_nb=0, **properties):  # msg pour afficher une alerte si mail erroné en pwreset par ex
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        
        # renseignements user 
        self.user = anvil.users.get_user(q.fetch_only("nom","prenom","role","email","enabled"))
        
        """
        self.bt_se_deconnecter.visible = False
        self.bt_user_mail.enabled = False
        self.column_panel_admin.visible = False
        """
        self.nb = nb
        """ Incrémentation de nb """
        self.nb = self.nb + 1
        if self.nb >= 99:  # retour de création de fiche renseignement, j'efface l'url pour arrêter la boucle
            h = {}

        """ cas 2: soit ouverture de l'app """
        """        ou retour par URL suite à PW reset ou confirm mail"""
        if self.nb == 2:
            self.column_panel_others.visible = False
            """ get_url_hash() gets the decoded hash (the part after the ‘#’ character) of the URL used to open this app.

                If the first character of the hash is a question mark (e.g., https://myapp.anvil.app/#?a=foo&b=bar),
                it will be interpreted as query-string-type parameters and returned as a dictionary
                (e.g., {'a': 'foo', 'b': 'bar'} ).

                get_url_hash() is available in Form code only.

                I don’t use extra arguments on forms loaded by the routing module.
                Using extra arguments kind of defeats the purpose of using the routing module.

                I pass all the arguments on the URL, then I use self.url_dict['items'].
                
                """

            h = {}
            h = anvil.get_url_hash()
            self.h = h
            # alert(f"h ds init d'AMS_Data: {h}")

            if len(h) != 0:  # a URL has openned this app
                # handling buttons display before going to module externe 'sign_in_for_AMS_Data'
                self.display_bt_mail()                 # Bt de connection
                self.display_admin_or_other_buttons()  # Autres BT
                
                # lien actif < à 3 mois ?
                # url_time_str=""
                url_time = h["t"]
                url_time_over = French_zone.time_over(url_time)
                if url_time_over:
                    alert("Ce lien n'est plus actif !")
                else:
                    # stage number in URL's Hash ? (le user vient-il de flacher le Qr code?)
                    # si oui je suis en sign in après flash du qr code par le stagiaire ou click du lien ds un mail
                    if "stage" in h:
                        self.qr_code()
                        return
                    if h["a"] == "pwreset":
                        self.pwreset()
                        return
                    if h["a"] == "confirm":
                        self.confirm()
                        return
        # handling buttons display
        self.display_bt_mail()
        self.display_admin_or_other_buttons()
        
        if not self.user:
            self.content_panel.clear()
        else:
            if self.user["prenom"] is None or self.user["prenom"] == "":
                self.column_panel_header.visible = False
                self.content_panel.add_component(Saisie_info_de_base(True), full_width_row=True)

    def pwreset(self, **event_args):
        # handling buttons display
        self.bt_user_mail.text = "Réinitialisation du mot de passe !"
        self.display_admin_or_other_buttons()
        self.bt_se_connecter.visible = False
        self.bt_sign_in.visible = False
        from sign_in_for_AMS_Data.url_from_mail_PW_reset import url_from_mail_PW_reset

        self.content_panel.clear()
        self.content_panel.add_component(
            url_from_mail_PW_reset(self.h["email"], self.h["api"]), full_width_row=True
        )
        return

    def confirm(self, **event_args):
        from sign_in_for_AMS_Data.url_from_mail_calls import url_from_mail_calls

        self.content_panel.clear()
        self.content_panel.add_component(
            url_from_mail_calls(self.h, num_stage=0), full_width_row=True
        )
        return

    # stage number in URL's Hash (le user vient de flasher le Qr code)
    # je suis en sign in après flash du qr code par le stagiaire ou click du lien ds un mail 
    def qr_code(self, **event_args):
        num_stage = self.h["stage"]   
        if "pour" in self.h:
            pour_stage = self.h["pour"]
        else:
            pour_stage = 0
            
        if len(num_stage) != 0:
            self.bt_sign_in_click(self.h, num_stage, pour_stage)
            return

    
    """ ***********************************************************************************************"""
    """ ****************************** Gestions  BOUTONS CONNECTION et leurs clicks ******************************"""
    """ ***********************************************************************************************"""
    def display_bt_mail(self, **event_args):
        if self.user:
            self.bt_user_mail.text = self.user["email"]
            self.column_panel_bt_mail.visible = True
            self.bt_se_connecter.visible = False
            self.bt_se_deconnecter.visible = True
        else:
            # Pas de USER
            self.bt_user_mail.text = "Non connecté"
            self.bt_user_mail.enabled = False
            self.bt_se_connecter.visible = True
            self.bt_sign_in.visible = True

            self.bt_se_deconnecter.visible = False
            self.outlined_card_niv1.visible = False
            self.column_panel_admin.visible = False
            self.column_panel_others.visible = False

    """ ***********************************************************************************************"""
    """ ****************************** Gestions  AUTRES BOUTONS et leurs clicks ******************************"""
    """ ***********************************************************************************************"""
    def display_admin_or_other_buttons(self, **event_args):
        if self.user:
            if self.user["enabled"] is False:
                alert("Not 'enabled' in table users")
                self.bt_sign_in.visible = False
                return

            self.bt_sign_in.visible = False
            self.bt_user_mail.enabled = True
            self.button_qcm.visible = True
            self.button_pre_requis.visible = True
            self.label_role.text = self.user['role']   # affichage du role

            if self.user["role"] == "S":
                self.column_panel_others.visible = True
                
            if self.user["role"] == "A" :                              # 'A'dministrator  JM    TOUT
                self.column_panel_admin.visible = True
                self.column_panel_others.visible = True
                self.flow_panel_admin_only.visible = True
                self.outlined_card_niv1.visible = True
                
            if self.user["role"] == "B":                    # Bureaux:   
                self.column_panel_bt_mail.visible = True        # se déconnecter
                self.outlined_card_pr_qcm.visible = True        
                self.button_qcm.visible = True                  # faire 1 qcm et voir ses résultats
                self.button_pre_requis.visible = True
                self.outlined_card_formulaires.visible = False  
                self.outlined_card_com.visible = False     

                self.column_panel_others.visible = True

                self.outlined_card_niv1.visible = True          # ds le panneau priv niveau 1 ...
                self.column_panel_formulaires.visible = True       # Voir les résultats des formulaires de suivi et de stisfaction     
                self.button_create_qcm.visible = True
                self.button_create_recherche.visible = True        # faire une recherche
                self.column_panel_events.visible = True            # Saisir et voir les évenemnts

            if self.user["role"] == "J":                    #  JC:   
                self.column_panel_bt_mail.visible = True        # se déconnecter
                self.outlined_card_pr_qcm.visible = False        
                self.button_pre_requis.visible = False
                
                self.outlined_card_formulaires.visible = False  
                self.outlined_card_com.visible = False           

                self.outlined_card_niv1.visible = True          # ds le panneau priv niveau 1 ...
                self.column_panel_formulaires.visible = False      
                self.button_create_qcm.visible = False
                self.button_create_recherche.visible = True     # faire une recherche
                self.column_panel_events.visible = True         # Saisir et voir les évenemnts

                
            if self.user["role"] == "T":                    # Tuteurs MotoN:   Juste Saisie Formulaire de suivi et pré requis
                self.outlined_card_pr_qcm.visible = True 
                self.button_pre_requis.visible = True           # Rentrer ses pré requis
                self.button_qcm.visible = False
                
                self.outlined_card_formulaires.visible = True   
                self.button_form_suivi_stage.visible = True     # Rentrer le formulaire de suivi de stage du stagiaire BPMotoN
                self.button_form_satisf.visible = False       # Rentrer le formulaire de fin de stage du stagiaire BPMotoN   ?????
                
                self.outlined_card_com.visible = False           

                self.outlined_card_niv1.visible = False   
                self.column_panel_formulaires.visible = False          
                self.button_create_qcm.visible = False
                self.button_create_recherche.visible = False

            if self.user["role"] == "F":                 # 1 Formateur peut .... 
                self.outlined_card_pr_qcm.visible = True        # faire 1 qcm et voir ses résultats 
                self.outlined_card_formulaires.visible = False  
                self.outlined_card_com.visible = True           # évaluer avec sa classe une intervention, voir ses propres résultats
                
                self.outlined_card_niv1.visible = True          # ds le panneau priv niveau 1 ...
                self.column_panel_formulaires.visible = False           
                self.button_create_qcm.visible = True           # créer un qcm
                self.button_create_recherche.visible = True     # rechercher un stagiaire
                
        else: #pas de user
            self.column_panel_bureaux.visible = False
            self.column_panel_admin.visible = False
            self.column_panel_others.visible = False
            
    # ===================================================================================================================
    #                                                                                                         BT 'SIGN IN'          
    # ===================================================================================================================
    def bt_sign_in_click(self, h={}, num_stage=0, pour_stage=0, **event_args):  # h qd vient de sign in par qr code
        """This method is called when the button is clicked"""
        from sign_in_for_AMS_Data.SignupDialog_V2 import SignupDialog_V2
        self.bt_user_mail.visible = False
        self.column_panel_2.visible = False
        self.content_panel.clear()        
        self.content_panel.add_component(SignupDialog_V2(h, num_stage, pour_stage), full_width_row=True)
        #open_form('sign_in_for_AMS_Data.SignupDialog_V2',h, num_stage, pour_stage)
    
    # ===================================================================================================================
    #                                                                                                 BT 'SE DECONNECTER'         
    # ===================================================================================================================
    def bt_se_deconnecter_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.content_panel.clear()
        anvil.users.logout()  # logging out the user
        self.user = None
        self.display_bt_mail()
        self.display_admin_or_other_buttons()
        
        
    # ===================================================================================================================
    #                                                                                                   BT 'SE CONNECTER'         
    # ===================================================================================================================
    def button_se_connecter_click(self, **event_args):
        """This method is called when the button is clicked"""
        """Will call the EXTERNAL MODULE DEPENDACY when the link is clicked"""
        self.bt_se_connecter.visible = False
        self.bt_sign_in.visible = False
        # import sign_in_for_AMS_Data
        from sign_in_for_AMS_Data.LoginDialog_V2 import LoginDialog_V2
        self.content_panel.clear()
        self.content_panel.add_component(LoginDialog_V2(), full_width_row=False)

    # click sur le mail du user (l'icone du petit bonhomme), envoi en "Saisie_info_apres_visu"
    def bt_user_mail_click(self, prem_util=False, **event_args):  # True=1ere utilisation
        self.content_panel.clear()
        self.bt_se_deconnecter.visible = False
        self.bt_sign_in.visible = False
        # Saisie_info_de_base(False) car pas la 1ere saisie de la fiche de renseignements
        if not self.user:
            self.content_panel.clear()
        else:
            open_form("Saisie_info_apres_visu", self.user["email"])

    # BT admin 'Stages' cliqué, envoi en "Visu_stages"         
    def bt_gestion_stages_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form("Visu_stages")

    # BT admin, Résultat des évaluations d'un stgiaire pour une date/intervention 
    def bt_com_1result_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_form_com_results_stagiaire_admin import Stage_form_com_results_stagiaire_admin
        open_form("Stage_form_com_results_stagiaire_admin")
    
    # BT admin, Résultat des évaluations d'une intervention 
    def bt_com_results_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_com_results_stagiaires import Stage_com_results_stagiaires
        open_form("Stage_com_results_stagiaires")
        
        
    # BT admin, Visu, maj, modif, del Saisie évenements
    def button_event_visu_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Evenements_visu_modif_del import Evenements_visu_modif_del
        open_form('Evenements_visu_modif_del')

    # BT stagiaire QCM
    def button_qcm_click(self, **event_args):
        from ..QCM_visu_modif_ST_Main import QCM_visu_modif_ST_Main
        open_form("QCM_visu_modif_ST_Main")

    # BT bureaux Recherches
    def button_create_recherche_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Recherche_stagiaire import Recherche_stagiaire
        open_form("Recherche_stagiaire")

    # BT stagiaire Doc requis à rentrer 
    def button_pre_requis_click(self, **event_args):
        from ..Pre_R_pour_stagiaire import Pre_R_pour_stagiaire
        open_form("Pre_R_pour_stagiaire")


    # BT Résultats des formulaires de suivi de stages
    def button_suivi_result_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_suivi_results import Stage_suivi_results
        open_form("Stage_suivi_results")

    # BT stagiaire pour son suivi de stage 
    def button_form_suivi_stage_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_form_suivi import Stage_form_suivi
        open_form("Stage_form_suivi")

    def button_parametres_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")  

    # BT Stagiaire, communication (avis du groupe sur une intervention)    
    def button_form_com_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_form_com import Stage_form_com
        open_form('Stage_form_com')

    # BT Stagiaire, communication (le stagiaire voit ses résultats (avis du groupe sur son intervention))
    def button_form_com_resultats_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Stage_form_com_results_stagiaire import Stage_form_com_results_stagiaire
        open_form('Stage_form_com_results_stagiaire')
        
    # BT résultats des formulaires de satisfaction en fin de stage
    def button_form_satisf_click(self, **event_args):
        from ..Stage_form_satisfaction import Stage_form_satisfaction
        open_form("Stage_form_satisfaction")

    # BT résultats des formulaires de satisfaction en fin de stage
    def button_satisf_result_click(self, **event_args):
        from ..Stage_satisf_statistics import Stage_satisf_statistics
        open_form("Stage_satisf_statistics")

    # BT Publipostage aux anciens stagiaires
    def button_mail_histo_click(self, **event_args):
        from ..Mail_to_old_stagiaires import Mail_to_old_stagiaires
        open_form("Mail_to_old_stagiaires")

    # BT UTILITAIRES 
    def bt_maj_txt_stagiaires_inscrits_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..z_Utilitaires_JM import z_Utilitaires_JM
        open_form('z_Utilitaires_JM')
        
    # BT Création/modif d'un QCM    
    def button_create_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..QCM_visu_modif import QCM_visu_modif
        open_form("QCM_visu_modif_Main")

    # Pour empêcher le msg session expired (suffit pour ordinateur, pas pour tel) 
    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        with anvil.server.no_loading_indicator:
            result = anvil.server.call("ping")
        print(f"ping on server to prevent 'session expired' every 5 min, server answer:{result}")

    
    #==============================================================
    # Les UTILITAIRES suivants sont à TRANSFERER DS UTILITAIRES POUR alléger module MAIN
    #==============================================================

    # ENVOI EN MODULE z_loop_on_tables pour plusieurs utilitaires
    def button_loop_click(self, **event_args):
        from .. import z_loop_on_tables
        result=z_loop_on_tables.loop_del_qcm5()
        alert(result)
    
    # Test pour fermer la fenêtre
    def Close_click(self, **event_args):
        import anvil.js
        from anvil.js.window import localStorage
        from anvil.js import window
        import anvil.users
        # Déconnecter l'utilisateur
        anvil.users.logout()
        # Afficher un message
        # alert("Vous êtes déconnecté.")
        window.close()

    # Génération d'un Qr code à partir d'une phrase, un lien, ...
    def button_qr_code_generator_click(self, **event_args):
        from ..QrCode_Generator import QrCode_Generator
        open_form("QrCode_Generator")

    
    # Extraction de fichier texte pour les qcm
    def button_txt_file_click(self, **event_args):
        # envoi en extraction des qcm à partir d'un fichier txt
        txt_msg = anvil.server.call("file_reading")
        alert(txt_msg)

    
    # Essai de signature électronique
    def button_sign_click(self, **event_args):
        from ..Signature import Signature
        open_form("Signature")

    # lecture d'un fichier csv (excel)
    def button_xls_click(self, **event_args):
        from ..XLS_reader import XLS_reader
        open_form("XLS_reader")

    
    # boucle sur les images dela table pré-requis pour resize jpg en 1000 x 800   ou 800 x 1000
    def button_rsz_img_click(self, **event_args):
        from ..Pre_R_Moulinette import Pre_R_Moulinette
        open_form("Pre_R_Moulinette")

    
    # (table PR stagiaire): calcul taille de l'img du pré-requis et écriture de cette taille ds le même row 
    def button_size_pr_click(self, **event_args):
        result = anvil.server.call('size_jpg')
        if result:
            alert("fin")
        else:
            alert("pas de fin normale")
            

   



    

   

    
    
    

    



    

