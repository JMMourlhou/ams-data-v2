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
        
        self.image.source = self.item['file']
        self.text_box_path.text = self.item['path']
        self.text_box_version.text = self.item['file_version']
        self.text_box_commentaires.text = self.item['commentaires']
        self.check_box_modif.checked = self.item['modifiable']
        self.check_box_annul.checked = self.item['annulable']
        # Any code you write here will run before the form opens.
        if file.