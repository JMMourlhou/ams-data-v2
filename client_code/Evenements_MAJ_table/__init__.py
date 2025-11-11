from ._anvil_designer import Evenements_MAJ_tableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Evenements_MAJ_table(Evenements_MAJ_tableTemplate):
    def __init__(self, **properties):  # row stagiaire inscrit, vient de pré_requis_pour stagiaire admin
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Nom du nouveau type d'évenement"
        self.text_box_3.placeholder = "1er message ex: 'Nouvel xxx'"
        self.text_box_4.placeholder = "2eme message ex: 'Voir un xxx'"
        self.text_area_1.placeholder = "Texte initial"
        # search de tous les pré-requis existants et affichage
        liste_tous = app_tables.event_types.search(
            tables.order_by("code", ascending=True),
        )
        self.nb = len(liste_tous)
        self.text_box_2.text = str(self.nb)  # le premier code commencant à 0, je n'ai pas à incrémenter += 1
        self.check_box_1.checked = False
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
        # Text_box_1 (type evnt) non vide
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 5:
            alert("Entrez un type d'évenement clair (> à 5 caractères")
            self.text_box_1.focus()
            return
        # Text_box_2 (code) non vide
        if self.text_box_2.text == "" or int(self.text_box_2.text) < (self.nb):
            alert("Entrez un code valide !")
            self.text_box_2.focus()
            return
        
        # Text_box_3 (msg 0)non vide
        if self.text_box_3.text == "" or len(self.text_box_3.text) < 6:
            alert("Entrez le message qui apparaîtra dans le menu ! (au moins 6 caractères)")
            self.text_box_3.focus()
            return
            
        # Text_box_4 (msg 1)non vide
        if self.text_box_4.text == "" or len(self.text_box_4.text) < 6:
            alert("Entrez le message qui apparaîtra dans le 2eme menu ! (au moins 6 caractères)")
            self.text_box_4.focus()
            return   
        
        # Code existant ?
        nb = int(self.text_box_2.text)
        row = app_tables.event_types.get(code = nb)
        if row:
            alert("Ce code est déjà pris !")
            self.text_box_2.focus()
            return
            
        r = alert("Voulez-vous vraiment ajouter ce Type d'évenement ?", dismissible=False, buttons=[("oui", True), ("non", False)],)
        if r:  # oui
            nb = int(self.text_box_2.text)
            result = anvil.server.call(
                "add_type_evnt",
                self.text_box_1.text,     # type devnt
                nb,                       # code (numérique)
                self.text_box_3.text,     # msg_1
                self.text_box_4.text,     # msg_2
                self.text_area_1.text,     # text_initial
                self.check_box_1.checked  # mot clé daté ?  True/ False
            )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Evenements_MAJ_table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True
