import anvil.tables as tables
#import anvil.tables.query as q
from anvil.tables import app_tables
from ._anvil_designer import Pre_Visu_imgTemplate
from anvil import *  # pour la notification

import anvil.server


class Pre_Visu_img(Pre_Visu_imgTemplate):
    def __init__(self, file, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.file = file
        self.f = get_open_form()
        self.image_1.source = file

    def retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)

    def download_click(self, **event_args):
        """This method is called when the button is clicked"""

        media = self.file
        anvil.media.download(media)
        n = Notification("Téléchargement effectué !", timeout=1)  # par défaut 2 secondes
        n.show()

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.download.scroll_into_view()
