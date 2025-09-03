from ._anvil_designer import ItemTemplate5Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate5(ItemTemplate5Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()
        # Any code you write here will run before the form opens.
        self.button_nom.text=self.item['name'].capitalize()+" "+self.item['prenom']


    def button_nom_click(self, **event_args):          # Click sur le BT nom/prénom pour voir ses pré requis
        """This method is called when the button is clicked"""

        if self.button_nom.background == "theme:Tertiary":
            self.button_nom.background = "red"
            #self.button_nom.foreground = "black"
        else:
            self.button_nom.background = "theme:Tertiary"
            #self.button_nom.foreground = "black"
        liste_pr = app_tables.pre_requis_stagiaire.search(
            tables.order_by("requis_txt", ascending=True),
            q.fetch_only("item_requis", "thumb", "stagiaire_email"),
            stagiaire_email = self.item['user_email'],        # user_email row
            stage_num = self.item['stage']                    # stage      row
        )
        self.repeating_panel_1.items = liste_pr
        if self.repeating_panel_1.visible is True:
            self.repeating_panel_1.visible = False
        else:
            self.repeating_panel_1.visible = True

    def button_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ...Pre_R_pour_1_stagiaire import Pre_R_pour_1_stagiaire
        open_form('Pre_R_pour_1_stagiaire',self.item)   # j'envoie le row 'stagiaire inscrit' en entier



 
        

            
