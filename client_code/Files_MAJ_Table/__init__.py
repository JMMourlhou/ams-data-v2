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
        self.button_add.visible = False

        
    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
        
    # Add -----------------------------------------------------------------------
    def button_add_file_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.file:
            r = alert(
                "Voulez-vous vraiment ajouter ce Fichier ?",
                dismissible=False,
                buttons=[("oui", True), ("non", False)],
            )
            if r:  # oui
                result, msg=anvil.server.call('add_file_table', self.file, self.file.name, self.text_box_commentaires.text, self.check_box_modif.checked, self.check_box_annul.checked)
                alert(msg)
                if result is False:
                    return
            open_form("Files_MAJ_Table")
        else:
            alert("Choisir un fichier !")
            return

    def file_loader_add_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.file = file
        self.image.source = file


    def image_show(self, **event_args):
        """This method is called when the Image is shown on the screen"""
        self.button_add_file.visible = True

    def text_box_commentaires_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.text_box_commentaires.placeholder = ""

   


    
    

    













        
