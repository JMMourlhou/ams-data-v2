from ._anvil_designer import list_modelesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Mail_subject_attach_txt
#import html  # pour échapper le texte brut si besoin

class list_modeles(list_modelesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
         # Any code you write here will run before the form opens.
        
        #import anvil.js    # pour screen size
        from anvil.js import window # to gain access to the window object
        screen_size = window.innerWidth
        if screen_size < 800:
            self.button_selection.text = ""


        
        self.text_area_subject.text = self.item['mail_subject']
        self.text_area_subject.tag.id = self.item.get_id() # je sauve l'id du modele mail row 
        
        # Pour rappel, rich_text au format html
        self.rich_text_html.format = "restricted_html"
        self.html_text = self.item['mail_text'] or ""  # Toujours une string
        self.rich_text_html.content = self.html_text
    
    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous enlever ce modèle de mail ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # Oui               
            anvil.server.call('del_mails', self.text_area_subject.tag.id) 
        self.f = get_open_form()   # récupération de la forme mère pour accéder aux fonctions et composents
        #print("form mère récupérable (delete): ", self.f)   
        # Je lis la liste d'emails, le ref du modèle, lt type de mail displayed, pour réaffichage
        type_mail = self.f.drop_down_type_mails.selected_value
        self.f.drop_down_type_mails_change(type_mail)
        """
        emails_liste = self.f.label_emails_liste.text
        ref_model = self.f.label_ref_model.text
        open_form('Mail_subject_attach_txt', emails_liste, ref_model) # réouverture pour réaffichage sans le modèle enlevé 
        """
    def text_area_subject_focus(self, **event_args):
        """This method is called when the button is clicked"""
        self.f = get_open_form()   # récupération de la forme mère 

        # si pas d'email liste, provenance mail du menu principal, je ne permets pas d'envoi de mail ou attachements
        
        if self.f.label_emails_liste.text == []:
            self.f.file_loader_attachments.visible = False
            self.f.button_sending.visible = False
            self.f.file_loader_attachments.visible = False
        else:
            self.f.file_loader_attachments.visible = True
            
        self.f.button_annuler.visible = False
        self.f.mode_creation = False
        self.f.button_new.visible = False
        self.f.column_panel_detail.visible = True # montre la form création/modif de modèle
        self.f.repeating_panel_1.visible = False # cache les modèles 
        
        self.f.label_id.text =  self.item.get_id() # récupère l'id du modele mail row (pour la modif en serveur)
        self.f.text_box_subject_detail.text = self.text_area_subject.text
        self.f.text_area_text_detail.text = self.item['mail_text'] # utilisé pour l'envoi du mail
        # appel du word editor
        self.f.call_word_editor(self.html_text, 'modif')
        
    """
    
    def call_word_editor(self, content_text_html, mode):
        from ...Word_editor import Word_editor   # Word processor component inséré ds self.content_panel
        title = "*** Modèle de Mail ***"
        sub_title = self.text_area_subject.text
        # INSERTION TEXT-EDITOR form 'Word_editor'  (voir import)
        text_editor = Word_editor()  
        text_editor.text = content_text_html   # .text: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        text_editor.param1 = mode              # mode 'modif'
        text_editor.top_ligne_1 = title              # pdf title when download 
        text_editor.top_ligne_2 = sub_title          # pdf sub_title when download 
        # y a til eu un changement dans le texte ? si oui affiche le bt validation
        text_editor.set_event_handler("x-text-changed-state", self._on_text_changed_state)

        # attendre que la forme fille soit pr^te pour gérer le bt_validation
        self._editor_ready = False
        text_editor.set_event_handler("x-editor-ready", self._arm_editor_ready)

        #text_editor.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 1 sec, timer_2 de la form Word_editor
        #text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 15 sec, timer_2 de la form Word_editor
        self.f.content_panel.add_component(text_editor)
        
   
    # RETOUR DU WORD EDITOR  
   
        
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form (modif du text de base de l'évènement)
    def _on_text_changed_state(self, sender, **e):
        if not self._editor_ready:
            return  # on ignore les events de chargement

        self.mode = sender.param1       # mode 'modif' /  'creation' 
        self.text = sender.text    # texte html de lévenement
        self.f.button_validation.visible = True 

        
        #if self.mode == "modif":
        #    self.button_modif_click(self.text)
        

    # handler por afficher le bouton validation uniqt qd text est modifié
    # ! self._editor_ready = False en création de la forme
    def _arm_editor_ready(self, **e):
        self._editor_ready = True    

    # Event raised every 1 sec: Automatic backup of the text in Word_editor form
    def timer_text_backup(self, sender, **event_args):
        alert(sender.text)
        
        # Toutes les 1 secondes, sauvegarde auto, self.id contient l'id du row qui est en cours de saisie
        with anvil.server.no_loading_indicator:
            self.f.button_validation_click("modif",sender.text) 
    
    """
    



