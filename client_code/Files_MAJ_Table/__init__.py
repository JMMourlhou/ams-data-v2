from ._anvil_designer import Files_MAJ_TableTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Files_MAJ_Table(Files_MAJ_TableTemplate):
    def __init__(
        self, **properties
    ):  # row stagiaire inscrit, vient de pré_requis_pour stagiaire admin
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
       
        # search de tous les files existants et affichage
        liste_tous = app_tables.files.search(
            tables.order_by("path", ascending=True),
        )
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
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 3:
            alert("Entrez un lieu valide!")
            self.text_box_1.focus()
            return
        # Text_box_2 non vide
        if self.text_box_2.text == "" or len(self.text_box_2.text) < 6:
            alert("Entrez une adresse supérieure à 5 caractères !")
            self.text_box_2.focus()
            return
        # Text_box_3 non vide
        """
        if self.text_box_3.text == "" or len(self.text_box_3.text) < 6:
            alert("Entrez un commentaire supérieur à 5 caractères !")
            self.text_box_3.focus()
            return
        """
        # Code existant ?
        row = app_tables.pre_requis.get(code_pre_requis=self.text_box_1.text)
        if row:
            alert("Ce lieu existe déjà !")
            self.text_box_1.focus()
            return
        r = alert(
            "Voulez-vous vraiment ajouter ce Lieu ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            result = anvil.server.call(
                "add_lieu",
                self.text_box_1.text,
                self.text_box_2.text,
                self.text_box_3.text,
            )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Lieux_MAJ_table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True
