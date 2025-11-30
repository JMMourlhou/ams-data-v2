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
        self.text_area_subject.text = self.item['mail_subject']
        self.text_area_subject.tag.id = self.item.get_id() # je sauve l'id du modele mail row 
        self.html_text = self.item['mail_text'] or ""  # Toujours une string
        self.text_area_1.text = self.item['mail_text']
        mail_html = self.item['mail_text'] or ""

        # IMPORTANT : on utilise .content, pas .text
        self.rich_text_html.format = "restricted_html"
        self.rich_text_html.content = mail_html
    
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
    def button_selection_click(self, **event_args):
        """This method is called when the button is clicked"""
        # récupération de la forme mère par  self.f = get_open_form() en init
        self.f = get_open_form()   # récupération de la forme mère pour accéder aux fonctions et composents

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
        self.f.text_area_text_detail.text = self.item['mail_text']
        # appel du word editor
        self.call_word_editor(self.text_area_1.text, 'modif')
        
    """
    =============================================================================================================================================      CALL FOR THE WORD EDITOR
    """
    def call_word_editor(self, content_text_html, mode):
        from ...Word_editor import Word_editor   # Word processor component inséré ds self.content_panel
        title = "*** Modèle de Mail ***"
        sub_title = self.text_area_subject.text
        # INSERTION TEXT-EDITOR form 'Word_editor'  (voir import)
        text_editor = Word_editor(title, sub_title)  # title/sub_title : pour le bt download 
        text_editor.text = content_text_html   # .text: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        text_editor.param1 = mode              # mode 'modif'
        text_editor.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        #text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 15 sec, timer_2 de la form Word_editor
        self.f.content_panel.add_component(text_editor)
        
    """
    #===================================================================================================================================================
    RETOUR DU WORD EDITOR  
    # ==================================================================================================================================================
    """
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form (modif du text de base de l'évènement)
    def handle_click_fin_saisie(self, sender, **event_args):
        # sender.text contains the 'Word_editor'form's HTML text
        mode = sender.param1       # mode 'modif' /  'creation' 
        self.text = sender.text    # texte html de lévenement
        if mode == "modif":
            self.f.button_modif_click(self.text)
        if mode == "exit":
            self.f.button_annuler_click()
    """
    Fin RETOUR DU WORD EDITOR  
    """  
    



