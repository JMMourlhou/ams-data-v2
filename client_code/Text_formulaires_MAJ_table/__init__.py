from ._anvil_designer import Text_formulaires_MAJ_tableTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Text_formulaires_MAJ_table(Text_formulaires_MAJ_tableTemplate):
    def __init__(
        self, **properties
    ):  # row stagiaire inscrit, vient de pré_requis_pour stagiaire admin
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Code"
        self.text_box_2.placeholder = "Texte"

        # search de tous les codes existants et affichage
        liste_tous = app_tables.texte_formulaires.search(
            tables.order_by("code", ascending=True),
        )
        self.repeating_panel_1.items = liste_tous

        # réaffichage des pré requis
        # open_form("Table_Pre_R_MAJ")

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
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 3:
            alert("Entrez un code valide!")
            self.text_box_1.focus()
            return
        # Text_box_2 non vide
        if self.text_box_2.text == "" or len(self.text_box_2.text) < 6:
            alert("Entrez un texte supérieur à 5 caractères !")
            self.text_box_2.focus()
            return
        # mise en majuscue du code    
        text = self.text_box_1.text
        self.text_box_1.text = text.upper()
        # Code existant ?
        row = app_tables.texte_formulaires.get(code=self.text_box_1.text)
        if row:
            alert("Ce code existe déjà !")
            self.text_box_1.focus()
            return
        r = alert(
            "Voulez-vous vraiment ajouter ce code ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            result = anvil.server.call(
                "add_text_formulaire",
                self.text_box_1.text,
                self.text_box_2.text,
                self.check_box_1.checked
            )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Text_formulaires_MAJ_table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True


