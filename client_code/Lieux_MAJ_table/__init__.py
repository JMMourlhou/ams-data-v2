from ._anvil_designer import Lieux_MAJ_tableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML

class Lieux_MAJ_table(Lieux_MAJ_tableTemplate):
    def __init__(self, **properties):  # row stagiaire inscrit, vient de pré_requis_pour stagiaire admin
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Lieu"
        self.text_box_2.placeholder = "Adresse"
        self.text_box_3.placeholder = "Commentaires"

        # search de tous les pré-requis existants et affichage
        liste_tous = app_tables.lieux.search(
            q.fetch_only("lieu", "adresse"),
            tables.order_by("lieu", ascending=True),
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
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 5:
            #alert("Entrez un lieu valide!")
            AlertHTML.error("Erreur", "Entrez un lieu valide (Plus de 4 caractères) !")
            self.text_box_1.focus()
            return
        # Text_box_2 non vide
        if self.text_box_2.text == "" or len(self.text_box_2.text) < 6:
            AlertHTML.error("Erreur", "Entrez une adresse supérieure à 5 caractères !")
            #alert("Entrez une adresse supérieure à 5 caractères !")
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
            #alert("Ce lieu existe déjà !")
            AlertHTML.error("Erreur", "Ce lieu existe déjà !")
            self.text_box_1.focus()
            return

        r = AlertConfirmHTML.ask(
            "Ajouter ce lieu ?",
            "<p>Voulez-vous vraiment ajouter ce lieu ?</p>",
            style="info",
            large = True
        )

        
        """
        r = alert(
            "Voulez-vous vraiment ajouter ce Lieu ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        """
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
            #alert("Création effectuée !")
            AlertHTML.success("Succès", "Création effectuée !")
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
