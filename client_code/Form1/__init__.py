from ._anvil_designer import Form1Template
from anvil import *


class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        
    @handle("", "show")
    def form_show(self, **event_args):
        url_text = "http://media.jmweb34.net:8080/Essai1_stream.mp4"
        self.video_1.source = url_text.url
        self.video_1.height=500
        self.video_1.width=1000