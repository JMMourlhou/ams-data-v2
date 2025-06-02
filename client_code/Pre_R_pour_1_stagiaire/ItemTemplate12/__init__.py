from ._anvil_designer import ItemTemplate12Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate12(ItemTemplate12Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.text = "  " + self.item['requis_txt']
        if self.item['thumb'] is not None:
            self.image_1.source = self.item['thumb']
        else:
            self.image_1.visible = False

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.item['doc1'] is not None:
            r=alert("Ce pré-requis n'est pas vide, Voulez-vous vraiment le détruire ?",dismissible=False,buttons=[("oui",True),("non",False)])
        else:
            r=alert("Voulez-vous détruire ce pré-requis ?", dismissible=False ,buttons=[("oui",True),("non",False)])
        if r :   # Oui               
            result = anvil.server.call('pr_stagiaire_del',self.item['stagiaire_email'], self.item['stage_num'], self.item['item_requis'], "destruction" )  # mode  destruction de PR pour ce stgiaire
            if not result:
                alert("Pré Requis non enlevé pour ce stagiaire")
            # réaffichage des pré requis : Trouver le row du stagiaire inscrit puis réouverture de la form "Pre_R_pour_1_stagiaire"
            row = app_tables.stagiaires_inscrits.get(   numero =     self.item['numero'],
                                                        user_email = self.item['stagiaire_email']
                                                        )
            # get_open_form() permet de ne prendre que la forme mère de la forme Pre_R_pour_1_stgiaire
            # et donc de ne pas avoir à réinitialiser la fome mère, ce qui fausserait sa self.f 
            self.maman = get_open_form()   # récupération de la forme appelante immédiate
            self.maman.display()

 
            