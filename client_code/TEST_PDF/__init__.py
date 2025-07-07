from ._anvil_designer import TEST_PDFTemplate
from anvil import *
import anvil.server
from anvil_extras.PageBreak import PageBreak

class TEST_PDF(TEST_PDFTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        media=anvil.server.call_s('test_pdf')
        anvil.media.download(media)