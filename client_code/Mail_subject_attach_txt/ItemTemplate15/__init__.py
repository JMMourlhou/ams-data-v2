from ._anvil_designer import ItemTemplate15Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Mail_subject_attach_txt

class ItemTemplate15(ItemTemplate15Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
         # Any code you write here will run before the form opens.
        self.text_area_subject.text = self.item['mail_subject']
        self.text_area_subject.tag.id = self.item.get_id() # je sauve l'id du modele mail row 
        self.text_area_text.text = self.item['mail_text']

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
        #print("form mère atteingnable (en modif): ", self.f) 

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
        self.f.text_area_text_detail.text = self.text_area_text.text



