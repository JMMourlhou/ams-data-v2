from ._anvil_designer import ImageItemTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ImageItem(ImageItemTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.page_label.visible = self.item['display_page_numbers']
        self.page_label.text = f'Page {self.item["page_number"]}'
        self.image.source = self.item['image']
    
        if self.item['add_border']:
            self.image.border = '1px solid'