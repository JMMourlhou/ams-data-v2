from ._anvil_designer import ItemTemplate31Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate31(ItemTemplate31Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.file = self.item['file']
        self.image.source = self.item['file']
        self.text_box_path.text = self.item['path']
        self.text_box_version.text = self.item['file_version']
        self.text_box_commentaires.text = self.item['commentaires']
        self.check_box_modif.checked = self.item['modifiable']
        self.check_box_annul.checked = self.item['annulable']
        # Any code you write here will run before the form opens.

    

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment effacer ce fichier ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result, msg = anvil.server.call("del_file_table", self.item)
            alert(msg)
            if result is False:
                return
        open_form("Files_MAJ_Table")

    def button_modif_file_click(self, **event_args):
        """This method is called when the button is clicked"""
        print(f"The file's name is: {self.file.name}")
        print(f"The number of bytes in the file is: {self.file.length}")
        print(f"The file's content type is: {self.file.content_type}")
        print(f"The file's contents[:15] are: '{self.file.get_bytes()[:15]}'")
        print(f'url: {self.file.url}')
        if self.file:
            r = alert(
                "Voulez-vous vraiment modifier ce Fichier ?",
                dismissible=False,
                buttons=[("oui", True), ("non", False)],
            )
            if r:  # oui
                result, msg=anvil.server.call('modif_file_table', self.file, self.item, self.file.name, self.text_box_commentaires.text, self.check_box_modif.checked, self.check_box_annul.checked)
                alert(msg)
                if result is False:
                    return
            open_form("Files_MAJ_Table")
        else:
            alert("Choisir un fichier !")
            return

    def file_loader_modif_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.file = file
        self.image.source = file   

    def image_show(self, **event_args):
        """This method is called when the Image is shown on the screen"""
        self.button_modif_file.visible = True

    def check_box_modif_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_file.visible = True

    def check_box_annul_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_file.visible = True

    def text_box_path_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif_file.visible = True

    def text_box_version_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif_file.visible = True

    def text_box_commentaires_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif_file.visible = True

 

    

    

    

    