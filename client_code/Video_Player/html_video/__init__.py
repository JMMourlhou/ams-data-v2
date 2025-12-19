from ._anvil_designer import html_videoTemplate
from anvil import *



class html_video(html_videoTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
