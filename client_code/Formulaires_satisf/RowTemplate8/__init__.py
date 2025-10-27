from ._anvil_designer import RowTemplate8Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate8(RowTemplate8Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        try:
            self.text_box_1.text = self.item['stage_num_txt']
            self.text_box_2.text = self.item['stage_row']['code_txt']
            try:
                nom_prenom = self.item['nom']+" "+self.item['prenom']
                self.text_box_3.text = nom_prenom
            except:
                self.text_box_3.text = self.item['nom']
        except:
            pass

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Attention ce formulaire va être effacé,\n\nConfirmez !", dismissible=False ,buttons=[("oui",True),("non",False)])
        if r :   # Oui
            result = anvil.server.call('del_formulaire_satisf', self.item)
            if not result:
                alert("Effacement du formulaire non effectué !")
                return
            open_form("Formulaires_satisf")