from ._anvil_designer import Stage_MAJ_TableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Stage_MAJ_Table(Stage_MAJ_TableTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

        self.text_box_1.placeholder = "Code stage"
        self.text_box_2.placeholder = "Intitulé"
        self.text_box_3.placeholder = "Type de stage (S/B/F/T/V)"

        # search de tous les stages existants et affichage
        liste_tous = app_tables.codes_stages.search(
            q.fetch_only("code", "intitulé", "type_stage"),
            tables.order_by("code", ascending=True),
        )
        self.repeating_panel_2.items = liste_tous

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
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 6:
            alert("Entrez un code valide!")
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
        row = app_tables.codes_stages.get(code=self.text_box_1.text)
        if row:
            alert("Ce stage existe déjà !")
            self.button_valid.visible = False
            self.text_box_1.focus()
            return
            
        r = alert(
            "Voulez-vous vraiment ajouter ce stage ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            result = anvil.server.call(
                "add_type_stage",
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
        open_form("Stage_MAJ_Table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True