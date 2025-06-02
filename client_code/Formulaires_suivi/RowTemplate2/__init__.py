from ._anvil_designer import RowTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate2(RowTemplate2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.text = self.item['stage_num_txt']
        self.text_box_2.text = self.item['stage_row']['code_txt']
        self.text_box_3.text = self.item['user_role']
        self.text_box_4.text = self.item['user_email']
        self.text_box_5.text = self.item['stagiaire_du_tuteur']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Attention ce formulaire va être effacé !", dismissible=False ,buttons=[("oui",True),("non",False)])
        if r :   # Oui
            result = anvil.server.call('del_formulaire_suivi', self.item)
            if not result:
                alert("Effacement du formulaire non effectué !")
                return
            open_form("Formulaires_suivi")