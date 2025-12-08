from ._anvil_designer import ItemTemplate12Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...AlertHTML import AlertHTML
from ...AlertConfirmHTML import AlertConfirmHTML

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
            r = AlertConfirmHTML.ask("Annulation d'un Pré-Requis : ", "Il y a un document pour ce P.Requis: Voulez-vous vraiment le détruire ?", style="error", large = True)
        else:
            r = AlertConfirmHTML.ask("Annulation d'un Pré-Requis : ", "Voulez-vous détruire ce P.Requis ?", style="error", large = True)
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

 
            