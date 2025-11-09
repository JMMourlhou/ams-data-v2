from ._anvil_designer import Pre_R_MAJ_tableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Pre_R_MAJ_table(Pre_R_MAJ_tableTemplate):
    def __init__(self, **properties):  # row stagiaire inscrit, vient de pré_requis_pour stagiaire admin
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Code ex: DIP-F-PSE"
        self.text_box_2.placeholder = "Intitulé"
        self.text_box_3.placeholder = "Commentaires"
        self.text_box_4.placeholder = "ordre ex: 1/2"
        
        
        # search de tous les pré-requis existants et affichage
        liste_tous_pr = app_tables.pre_requis.search(q.fetch_only("requis", "code_pre_requis"),
                                                        tables.order_by("requis", ascending=True)
                                                    )
        self.repeating_panel_1.items = liste_tous_pr


        # réaffichage des pré requis
        #open_form("Table_Pre_R_MAJ")

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_add.visible = True
        

    def button_valid_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Text_box_1 non vide
        if self.text_box_1.text == "" or len(self.text_box_1.text)<3:
            alert("Entrez un code de Pré-Requis valide!")
            self.text_box_1.focus()
            return
        # Text_box_2 non vide
        if self.text_box_2.text == "" or len(self.text_box_2.text)<6:
            alert("Entrez un intitulé supérieur à 5 caractères !")
            self.text_box_2.focus()
            return
            
        # Text_box_4 (order) non vide
        if self.text_box_4.text == "" :
            alert("Entrez le num de page / nb de pages    ex: 1/2")
            self.text_box_4.focus()
            return
        # Code existant ?
        row = app_tables.pre_requis.get(code_pre_requis=self.text_box_1.text) 
        if row:
            alert("Ce code de Pré-Requis existe déjà !")
            self.text_box_1.focus()
            return
        r=alert("Voulez-vous vraiment ajouter ce Pré-Requis ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            code = self.text_box_1.text.upper() # mettre en majuscule le code
            result = anvil.server.call("add_pr", code, self.text_box_4.text, self.text_box_2.text, self.text_box_3.text )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Pre_R_MAJ_table")
        
    
    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True
    
    