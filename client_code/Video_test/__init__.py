from ._anvil_designer import Video_testTemplate
from anvil import *


class Video_test(Video_testTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.video_player_1.video_url = (
            "http://media.jmweb34.net:8080/Essai1_stream.mp4"
        )