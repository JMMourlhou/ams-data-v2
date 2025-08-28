from ._anvil_designer import Stage_visu_modifTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from .. import French_zone

class Stage_visu_modif(Stage_visu_modifTemplate):
    def __init__(self, num_stage=0, bg_task=False, **properties):     # bg_task True: je crée les bg task en entrée de stage visu modif
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.num_stage=num_stage
        self.bg_task = bg_task
        
        self.f = get_open_form()   # récupération de la forme mère pour revenir ds la forme appelante
        print("form mère atteingnable (en modif): ", self.f)
      
        # Any code you write here will run before the form opens.
        if num_stage == 0:
            #alert("Numéro de stage non trouvé")
            return
        
        # Drop down codes stages
        self.drop_down_code_stage.items = [(r['code'], r) for r in app_tables.codes_stages.search(tables.order_by("code", ascending=True))]

        # Drop down codes lieux
        self.drop_down_lieux.items = [(r['lieu'], r) for r in app_tables.lieux.search()]

        # drop_down mode fi pour le repeat_panel de Stage_visu_modif (si je clique sur l'historique, je vais visualise le stage)
        # comme j'utilise le get_open_form() en stage_visu_modif, je dois insérer ici en recherche ET en Stage_visu_modif le drop down des modees de fi
        self.drop_down_mode_fi.items = [(r['code_fi'], r) for r in app_tables.mode_financement.search(tables.order_by("code_fi", ascending=True))]
        
        #lecture du stage
        self.stage_row=app_tables.stages.get(numero=int(num_stage))
        
        
        #lecture des stagiaires inscrits
        liste_stagiaires = app_tables.stagiaires_inscrits.search(   q.fetch_only("name", "prenom", "financement", "numero", user_email=q.fetch_only("email", "tel")),
                                                                    tables.order_by("name", ascending=True),
                                                                    stage=self.stage_row
                                                                           )
        if len(liste_stagiaires) > 0:                      # des stagiaires sont déjà inscrits ds stage
            self.repeating_panel_1.items = liste_stagiaires
        else:                                              # stage vide, je n'affiche pas les bt et la liste
            self.button_trombi.visible = False

            
        #lecture intitulé stage
        self.intitul = self.stage_row['code']['code']
        type_row = app_tables.codes_stages.get(code=self.intitul)
        if type_row:
            intit = type_row['intitulé']
        else:
            alert("intitulé du stage non trouvé !")
            return
        
        if self.stage_row:
            self.text_box_num_stage.text = self.stage_row['numero']
            self.drop_down_code_stage.selected_value = self.stage_row['code']
            self.text_box_intitule.text = intit
            self.date_picker_from.date = self.stage_row['date_debut']
            self.text_box_nb_stagiaires_deb.text = self.stage_row['nb_stagiaires_deb']
            self.date_picker_to.date = self.stage_row['date_fin']
            self.text_box_nb_stagiaires_fin.text = self.stage_row['nb_stagiaires_fin']
            self.text_box_nb_stagiaires_diplom.text = self.stage_row['nb_stagiaires_diplomes']
            self.text_area_commentaires.text = self.stage_row['commentaires']
            self.drop_down_lieux.selected_value = self.stage_row['lieu']
            self.check_box_allow_bg_task.checked = self.stage_row['allow_bgt_generation']
            self.check_box_allow_satisf.checked = self.stage_row['saisie_satisf_ok']
            self.check_box_allow_suivi.checked = self.stage_row['saisie_suivi_ok']
            self.check_box_allow_com.checked = self.stage_row['display_com']
            
            
            """ *************************************************************************"""
            """       Création de liste et trombi en back ground task si stagiaires ds stage     """
            """ ***********************************************************************"""            
            if self.check_box_allow_bg_task.checked is False or self.bg_task is True:     # ex: en retour de trombi, pas besoin de re-générer les listes
                students_rows = list(app_tables.stagiaires_inscrits.search( q.fetch_only(),
                                                                            stage=self.stage_row))
                #alert(len(students_rows))
                if students_rows:    # stagiaires existants
                    """
                    #with anvil.server.no_loading_indicator:
                    self.task_list = anvil.server.call_s('run_bg_task_stage_list',self.text_box_num_stage.text, self.text_box_intitule.text)
                    self.timer_1.interval=0.5
                    
                    #with anvil.server.no_loading_indicator:
                    self.task_trombi = anvil.server.call_s('run_bg_task_trombi',self.text_box_num_stage.text, self.text_box_intitule.text)
                    self.timer_2.interval=0.5
                    """
        else:
            alert("Stage non trouvé")
            return

    def date_picker_to_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        date1 = self.date_picker_to.date
        date2 = self.date_picker_from.date
        if date1 < date2:
            alert("La date de fin est inférieure à la date de début !")
            self.date_picker_to.focus()
        
    def date_picker_from_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        date1 = self.date_picker_to.date
        date2 = self.date_picker_from.date
        if date1 < date2:
            alert("La date de fin est inférieure à la date de début !")
            self.date_picker_to.focus()
    
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Je connais la forme appelante: en init : self.f = get_open_form()
        if str(self.f) != str(self) and self.button_validation.visible is not True:
            open_form(self.f)
        else:
            from ..Visu_stages import Visu_stages
            open_form("Visu_stages")

        
    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        """ Tests avant validation """

        row = self.drop_down_code_stage.selected_value    # Récupération de la ligne stage sélectionnée
        if row is None:
            alert("Entrez le code du stage")
            return
        row2 = self.drop_down_lieux.selected_value         # Récupération du lieu sélectionné
        if row2 is None:
            alert("Entrez le lieu du stage")
            return

        if self.date_picker_to.date is None :           # dates vides ?
            alert("Entrez la date de fin du stage")
            return
        if self.date_picker_from.date is None :
            alert("Entrez la date de début du stage")
            return

        # Test si numero stage code existant pour permettre la modif
        stage=None
        stage = app_tables.stages.search(numero=int(self.text_box_num_stage.text))
        if len(stage) == 0:
            alert("Le numéro de stage n'existe pas !")
            self.button_annuler_click()

        # ! modif du  num de stage possible !!!
        result = anvil.server.call("modif_stage", row,
                                                self.text_box_num_stage.text,  # num du stage  de la ligne  
                                                row2['lieu'],                                              
                                                self.date_picker_from.date,
                                                self.text_box_nb_stagiaires_deb.text,
                                                self.date_picker_to.date,
                                                self.text_box_nb_stagiaires_fin.text,
                                                self.text_box_nb_stagiaires_diplom.text,
                                                self.text_area_commentaires.text,
                                                self.check_box_allow_bg_task.checked,
                                                self.check_box_allow_satisf.checked,
                                                self.check_box_allow_suivi.checked,
                                                self.check_box_allow_com.checked
                                                 )
        if result is True :
            alert("Stage mis à jour !")
        else :
            alert("Stage non modifié !")
        self.button_annuler_click()

   
    def drop_down_lieux_change(self, **event_args):
        """This method is called when an item is selected"""
        self.button_validation.visible = True
        
    def text_box_nb_stagiaires_deb_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True

    def text_box_nb_stagiaires_fin_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True

    def text_box_nb_stagiaires_diplom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True

    def text_area_commentaires_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.button_validation.visible = True
        
    def check_box_allow_bg_task_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_validation.visible = True   

    def check_box_allow_satisf_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # si check box F_satisf validé: test si un dict de satisf existe pour ce stage 
        if self.check_box_allow_satisf.checked is True:
            # lecture de table mère 'code_stage' pour verif si un dict template existant
            code_stage_row = app_tables.codes_stages.get(code=self.stage_row['code']['code'])
            if code_stage_row['satisf_q_ferm_template'] != {}:
                r=alert(f"Voulez-vous authoriser l'utilisation du formulaire de satisfaction {self.stage_row['code']['code']} existant pour les stagiaires de ce stage ?", dismissible=False ,buttons=[("oui",True),("non",False)])
                if r :   # Oui
                    # copie du formulaire de satisfaction de table code_stages vers la table stage pour ce stage
                    anvil.server.call("update_satisf_pour_un_stage",self.stage_row, code_stage_row['satisf_q_ouv_template'], code_stage_row['satisf_q_ferm_template'])
            else:
                alert(f"Attention, pas de formulaire de satisfaction {self.stage_row['code']['code']} encore créé !\n\nCréez d'abord un formulaire de satisfaction pour ce type de stage (Dans les Paramètres)")
                self.check_box_allow_satisf.checked = False
                self.button_validation.visible = False
                return
        else:
            self.button_validation.visible = True
            self.column_panel_header.scroll_into_view()

    def check_box_allow_suivi_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # si chck box F_suivi validé: test si un dict de suivi existe pour ce stage 
        if self.check_box_allow_suivi.checked is True:
            # lecture de table mère 'code_stage' pour verif si un dict template existant
            code_stage_row = app_tables.codes_stages.get(code=self.stage_row['code']['code'])
            if code_stage_row['suivi_stage_q_ferm_template'] != {}:
                r=alert(f"Voulez-vous authoriser l'utilisation du formulaire de suivi {self.stage_row['code']['code']} existant pour les stagiaires de ce stage ?", dismissible=False ,buttons=[("oui",True),("non",False)])
                if r :   # Oui
                    # copie du formulaire de suivi de table code_stages vers la table stage pour ce stage
                    anvil.server.call("update_suivi_pour_un_stage",self.stage_row, code_stage_row['suivi_stage_q_ouv_template'], code_stage_row['suivi_stage_q_ferm_template'])
            else:
                alert(f"Attention, pas de formulaire de suivi {self.stage_row['code']['code']} encore créé !\n\nCréez d'abord un formulaire de suivi pour ce type de stage (Dans les Paramètres)")
                self.check_box_allow_suivi.checked = False
                self.button_validation.visible = False
                return
        else:
            self.button_validation.visible = True
            self.column_panel_header.scroll_into_view()

    def check_box_allow_com_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # si check box F_com validé: test si un dict de com existe pour ce stage 
        if self.check_box_allow_com.checked is True:
            # lecture de table mère 'code_stage' pour verif si un dict template existant
            code_stage_row = app_tables.codes_stages.get(code=self.stage_row['code']['code'])
            if code_stage_row['com_ferm'] != {}:
                r=alert(f"Voulez-vous authoriser l'utilisation du formulaire de communication {self.stage_row['code']['code']} existant pour les stagiaires de ce stage ?", dismissible=False ,buttons=[("oui",True),("non",False)])
                if r :   # Oui
                    # copie du formulaire de communication de table code_stages vers la table stage pour ce stage
                    anvil.server.call("update_com_pour_un_stage",self.stage_row, code_stage_row['com_ouv'], code_stage_row['com_ferm'])
            else:
                alert(f"Attention, pas de formulaire de communication {self.stage_row['code']['code']} encore créé !\n\nCréez d'abord un formulaire de com pour ce type de stage (Dans les Paramètres)")
                self.check_box_allow_com.checked = False 
                self.button_validation.visible = False
                return
        else:
            self.button_validation.visible = True
            self.column_panel_header.scroll_into_view()

    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_trombi import Visu_trombi
        open_form('Visu_trombi',self.text_box_num_stage.text, self.text_box_intitule.text, False, None, False)

       
    def button_list_pdf_stagiaires_click(self, **event_args):
        """This method is called when the button is clicked"""
        stage_row = app_tables.stages.get(numero=int(self.num_stage))
        pdf = stage_row['list_media']
        if pdf:
            anvil.media.download(pdf)
            alert("Liste téléchargée")
        else:
            alert("Liste du trombi non trouvée")

    def button_qr_code_display_click(self, **event_args):
        """This method is called when the button is clicked"""
        # False indique que ce n'est pas une invitation à log in normal
        # mais une invitation à s'inscrire au stage
        open_form('QrCode_display', False, self.text_box_num_stage.text)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.column_panel_header.scroll_into_view()

    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.task_list.is_completed():
            self.button_fiches_stagiaires.visible = True
            self.timer_1.interval=0
            anvil.server.call('task_killer',self.task_list)

            
    def timer_2_tick(self, **event_args):
        if self.task_trombi.is_completed():
            self.timer_2.interval=0
            anvil.server.call('task_killer',self.task_trombi)

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        self.button_validation.visible = True   
        row = self.drop_down_code_stage.selected_value
        if row is None :
            alert("Vous devez sélectionner un stage !")
            self.drop_down_code_stage.focus()
            return
        self.text_box_intitule.text=row['intitulé']

    def button_qr_code_display_copy_click(self, **event_args):
        """This method is called when the button is clicked"""
        num_stage = self.text_box_num_stage.text
        if num_stage != "1003":
            n = Notification("Recherchez le Stagiaire ou Formateur à inscrire", timeout=1)   # par défaut 2 secondes
        else:
            n = Notification("Recherchez le Tuteur à inscrire", timeout=1)   # par défaut 2 secondes
        n.show()
        open_form('Recherche_stagiaire',num_stage)

    






        

    

    

    
    
  

    







                                    
