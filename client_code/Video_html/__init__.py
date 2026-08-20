from ._anvil_designer import Video_htmlTemplate
from anvil import *
import anvil.server

class Video_html(Video_htmlTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

