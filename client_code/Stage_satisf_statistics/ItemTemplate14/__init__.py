from ._anvil_designer import ItemTemplate14Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate14(ItemTemplate14Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings. 
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.button_mail.tag = self.item['user_email']
        #erreur si tel vide
        try:
            self.text_box_1.text = self.item['name']+" "+self.item['prenom']+" "+self.item['user_email']['tel']
        except:
            self.text_box_1.text = self.item['name']+" "+self.item['prenom']
            
            
    def button_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        liste_email = []
        liste_email.append((self.button_mail.tag['email'],self.button_mail.tag['prenom'],""))   # mail et prénom, id pas besoin
       
        # 'formul' indique l'origine, ici 'formulaire de satisfaction'
        from ...Mail_subject_attach_txt import Mail_subject_attach_txt

        # liste email contient:   mail txt, prénom txt 
        open_form("Mail_subject_attach_txt",  liste_email, 'formul') 
        






        
        