from ._anvil_designer import Global_Variables_MAJ_tableTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Global_Variables_MAJ_table(Global_Variables_MAJ_tableTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Variable glob."
        self.text_box_2.placeholder = "Valeur"
        self.text_box_3.placeholder = "Commentaires"

        # search de tous les stages existants et affichage
        liste_tous = app_tables.global_variables.search(tables.order_by("name", ascending=True))
        self.repeating_panel_1.items = liste_tous

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
        if self.text_box_1.text == "" :
            alert("Entrez un code valide!")
            self.text_box_1.focus()
            return
        # Text_box_2 non vide
        if self.text_box_2.text == "" :
            alert("Entrez un intitulé supérieur à 5 caractères !")
            self.text_box_2.focus()
            return
        # Text_box_3 non vide
        """
        if self.text_box_3.text == "" or len(self.text_box_3.text) < 6:
            alert("Entrez un commentaire supérieur à 5 caractères !")
            self.text_box_3.focus()
            return
        """
        # Nom variable globale existant ?
        row = app_tables.global_variables.get(name=self.text_box_1.text)
        if row:
            alert("Ce nom de var globale existe déjà !")
            self.button_valid.visible = False
            self.text_box_1.focus()
            return
            
        r = alert("Voulez-vous vraiment ajouter cette variable globale ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            result = anvil.server.call("add_global_variables",
                self.text_box_1.text,
                self.text_box_2.text,
                self.text_box_3.text,
            )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                self.button_valid.visible = False
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Global_Variables_MAJ_table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True