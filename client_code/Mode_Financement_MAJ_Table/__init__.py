from ._anvil_designer import Mode_Financement_MAJ_TableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Mode_Financement_MAJ_Table(Mode_Financement_MAJ_TableTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Code financement"
        self.text_box_2.placeholder = "Intitulé"
        self.text_box_3.placeholder = "Commentaires"

        # search de tous les mode fi existants et affichage
        liste_tous = app_tables.mode_financement.search(
            q.fetch_only("code_fi", "intitule_fi"),
            tables.order_by("code_fi", ascending=True),
        )
        self.repeating_panel_1.items = liste_tous

 
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_add.visible = True
        self.text_box_1.focus()

    def button_valid_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Text_box_1 non vide
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 2:
            alert("Entrez un code de mode de financement correct (2 caractères minimum)")
            self.text_box_1.focus()
            return
        # Text_box_2 non vide
        if self.text_box_2.text == "" or len(self.text_box_2.text) < 6:
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
        # Code existant ?
        row = app_tables.mode_financement.get(code_fi=self.text_box_1.text)
        if row:
            alert("Ce mode de financement existe déjà !")
            self.text_box_1.focus()
            return
        r = alert(
            "Voulez-vous vraiment ajouter ce mode de financement ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            result = anvil.server.call(
                "add_mode_fi",
                self.text_box_1.text,
                self.text_box_2.text
            )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Mode_Financement_MAJ_Table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True