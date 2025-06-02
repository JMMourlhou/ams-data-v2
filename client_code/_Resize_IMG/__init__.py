from ._anvil_designer import _Resize_IMGTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class _Resize_IMG(_Resize_IMGTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.label_1.text = file.length
        self.label_1_nom.text = file.name
        
        file_rezized = anvil.server.call('resize_img',file, file.name)
        self.image_1.source = file_rezized
        
        self.label_2.text = file_rezized.length
        self.label_2_nom.text = file_rezized.name
        if file_rezized:
            anvil.media.download(file_rezized)
            alert("img jpg téléchargée !")
        else:
            alert("img jpg non générée")