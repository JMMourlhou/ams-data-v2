from ._anvil_designer import Mail_subject_attach_txtTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML
from ..Word_editor import Word_editor   # Word processor component inséré ds self.content_panel

# emails_liste liste des mails
# ref_model contient lea ref du modele de mail si vient de qcm ou formul satisf ou recherche etc...du permet de court circuiter la drop down du choix du modèle 
class Mail_subject_attach_txt(Mail_subject_attach_txtTemplate):
    def __init__(self, emails_liste=[], ref_model = "", old_stagiaires = False, **properties): 
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()
        self.old_stagiaires = old_stagiaires
        self.ref_model = ref_model
        self.emails_liste = emails_liste # liste des mails
       
        # Récupération des icones ds files pour afficher les icones en template 16
        self.icone_xls = app_tables.files.get(path="logo_xls.jpg")['file'] # lit la colonne 'file', media object
        self.icone_doc = app_tables.files.get(path="logo word.jpg")['file']
        self.icone_ppt = app_tables.files.get(path="logo_ppt.jpg")['file']
        self.icone_pdf = app_tables.files.get(path="logo pdf.jpg")['file']
        
        self.dico_attachements = {}                # initialisation du dict des attachements
        self.list_attach = []          # initialisation de la liste des attachements
    
        
        #print('ref_model: ',self.ref_model)   
      
        self.mode_creation = False

        self.label_ref_model.text = ref_model # sauve la ref de modèle de mail
        
        
        #print('emails liste: ', self.emails_liste)
        self.label_emails_liste.text = emails_liste   # sauve la liste de mails à envoyer, (utilisé ds le item repeating panel, del)

        
        # import anvil.js    # pour screen size
        from anvil.js import window  # to gain access to the window object

        global screen_size
        screen_size = window.innerWidth

        # INITIALISATION Drop down   drop_down_type_mails
        self.drop_down_type_mails.items = [(r['type_mail'], r) for r in app_tables.mail_type.search(tables.order_by("type_mail", ascending=True))]
        
        # ref_model en init contient la ref du modele si vient de qcm ou formul etc...du permet de court circuiter la drop down du choix du modèle 
        if self.ref_model != "":
            # lecture du modele pour court circuiter la drop down du choix du modèle 
            type_mail_row = app_tables.mail_type.get(ref=self.ref_model)
            #print("ok: ", type_mail_row['type_mail'])
            if type_mail_row:
                self.drop_down_type_mails.selected_value = type_mail_row
                self.drop_down_type_mails_change(type_mail_row)

    def drop_down_type_mails_change(self, type_mail_row=None, **event_args): 
        #si j'ai court circuiter le dropdown (car vient de qcm, form satisf, recherche stag, ...) 
        if type_mail_row is None:
            type_mail_row = self.drop_down_type_mails.selected_value
            #self.ref_model = type_mail_row['ref']
            
        liste_mails =  app_tables.mail_templates.search(
                                                        tables.order_by("last_modif_date", ascending=False),
                                                        type = type_mail_row
                                                        )
        self.repeating_panel_1.visible = True
        self.repeating_panel_1.items = liste_mails
        
        self.content_panel.clear()  #effacement du content_panel

        self.column_panel_detail.visible = False
        self.file_loader_attachments.visible = True
        self.button_sending.visible = True
        self.button_new.visible = True
        self.button_annuler.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f) 
        
    

    def button_sending_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Confirmez-vous l'envoi ?",dismissible=False, buttons=[("oui",True),("non",False)])
        if r :   # Oui    
            liste_des_attachements = list(self.dico_attachements.keys()) # extraction des clefs du dico des attachements

            self.task_mail = anvil.server.call("run_bg_task_mail",self.emails_liste, self.text_box_subject_detail.text, self.text_area_text_detail.text, liste_des_attachements, self.old_stagiaires)
            self.timer_1.interval=0.5
            

    def text_box_subject_detail_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_validation.visible = True
        
    def text_area_text_detail_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.text_box_subject_detail_change()

    def button_new_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        self.column_panel_detail.visible = True # panel création visible
        self.repeating_panel_1.visible = False      # panel des modèles invisible
        self.repeating_panel_2.visible = False      # panel des attachements invisible
        self.file_loader_attachments.visible = False
        self.button_sending.visible = False
        self.mode_creation = True
        self.text_box_subject_detail.text = "Entrez ici le Nom de ce modèle"
        self.text_box_subject_detail.focus()
       
        # appel du word editor
        self.call_word_editor("Entrer le nouveau texte ici", 'creation')

    """
    =============================================================================================================================================      CALL FOR THE WORD EDITOR
    """
    def call_word_editor(self, content_text_html, mode):
        # INSERTION TEXT-EDITOR form 'Word_editor'  (voir import)
        text_editor = Word_editor()
        if mode == "creation":
            title = "*** Nouveau Modèle de Mail ***"
            sub_title = ""
            text_editor.text = "Le prénom est déjà prévu"                        # .text: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        else:
            title = "*** Modèle de Mail ***"
            sub_title = ""
            text_editor.text = content_text_html
            
        text_editor.param1 = mode                    # mode 'creation' / "modif"
        text_editor.top_ligne_1 = title              # pdf title when download 
        text_editor.top_ligne_2 = sub_title          # pdf sub_title when download 

        # y a til eu un changement dans le texte ? si oui affiche le bt validation
        text_editor.set_event_handler("x-text-changed-state", self._on_text_changed_state)

        # attendre que la forme fille soit pr^te pour gérer le bt_validation
        self._editor_ready = False
        text_editor.set_event_handler("x-editor-ready", self._arm_editor_ready)
        
        #text_editor.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 1 sec, timer_2 de la form Word_editor
        
        self.content_panel.add_component(text_editor)

    """
    #===================================================================================================================================================
    RETOUR DU WORD EDITOR  
    # ==================================================================================================================================================
    """
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form (modif du text de base de l'évènement)
    def _on_text_changed_state(self, sender, **e):
        if not self._editor_ready:
            return  # on ignore les events de chargement
            
        self.mode = sender.param1       # mode 'modif' /  'creation' 
        self.text = sender.text    # texte html de lévenement
        self.button_validation.visible = True 
       
       

    # handler por afficher le bouton validation uniqt qd text est modifié
    # ! self._editor_ready = False en création de la forme
    def _arm_editor_ready(self, **e):
        self._editor_ready = True    

    # Event raised every 1 sec: Automatic backup of the text in Word_editor form
    
    def timer_text_backup(self, sender, **event_args):
        # Toutes les 1 secondes, sauvegarde auto du texte en mémoire par sur table
        self.mode_sov = sender.param1       # mode 'modif' /  'creation' 
        self.text_sov = sender.text
       

    def button_validation_click(self, **event_args):   
        self.validation(self.mode_sov, self.text_sov) 
        
    def validation(self, mode, html_text="", **event_args):   
        result = ""
        if mode=="creation":  # Création du modèle
            if not self.drop_down_type_mails.selected_value:
                alert("Sélectionnez le type de modèle")
                return
            #r=alert("Enregistrer ce modèle ?",buttons=[("oui",True),("non",False)])
            #if r :   # Oui               
            result = anvil.server.call('add_mail_model', self.drop_down_type_mails.selected_value,self.text_box_subject_detail.text, html_text)
        
        if mode=="modif":  # Création du modèle
            #r=alert("Modifier ce modèle ?",buttons=[("oui",True),("non",False)])
            #if r :   # Oui               
            result = anvil.server.call('modify_mail_model',self.label_id.text,self.text_box_subject_detail.text, html_text)
            
        if result is False:
            if mode=="creation":  # Création du modèle
                alert("Modèle de mail non créé")
            else:
                alert("Modèle de mail non modifié")
        # Si bt validation a bien été cliqué (sov_auto = False)
        
        
        self.content_panel.clear()
        self.mode_sov = ""       # mode 'modif' /  'creation' 
        self.text_sov = ""
        self.column_panel_detail.visible = False   # effact du panel de création/modif
        self.button_validation.visible = False
        #self.file_loader_attachments.visible = True
        self.drop_down_type_mails_change(self.drop_down_type_mails.selected_value)   
        
    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Abandon en création ou modif de modèle
        self.content_panel.clear()
        self.button_annuler.visible = True
        self.button_new.visible = True
        self.column_panel_detail.visible = False # cache la form création/modif de modèle
        self.repeating_panel_1.visible = True # remontre les modèles 

    def file_loader_attachments_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""

        if file is not None:  #pas d'annulation en ouvrant choix de fichier
            self.list_attach = [] # réinitialisation de la liste pour le repeating panel
            # insertion ds le dictionaire liste_attachements et création de la liste correspondante pour le repeating panel
            
            
            clef = file         # media object du fichier est la clé du dict 
            valeur = file.name   # valeur est le nom du dict
            #print("clef: ",clef, "     valeur: ", valeur)
            self.dico_attachements[clef] = valeur   # je mets à jour le dico des attachements media_file : file_name_txt

            for clef, valeur in self.dico_attachements.items():
                self.list_attach.append((clef,valeur))  # transformation dict en liste pour le repeating panel
            
            #affichage image
            self.repeating_panel_2.visible = True
            self.repeating_panel_2.items = self.list_attach

            
    # Mails
    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        try:
            if self.task_mail.is_completed():
                self.timer_1.interval=0
                anvil.server.call('task_killer',self.task_mail)
                
                # lit le nb de mails ds table temp
                nb_mails = app_tables.temp.search()[0]['nb_mails_sent']
                if nb_mails == 1:
                    msg = "1 mail envoyé"
                else:
                    msg = str(nb_mails)+" mails envoyés"
                AlertHTML.success("Réussite :", msg)
             
            self.button_retour_click()
        except Exception as e:
            AlertHTML.error("Erreur :", f"Erreur lors d'envoi de mail{e}")

        