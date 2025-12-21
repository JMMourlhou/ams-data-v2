from ._anvil_designer import Video_PlayerTemplate
from anvil import *

class Video_Player(Video_PlayerTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        self.video_html_1.video_url = "https://media.jmweb34.net/Essai1_stream.mp4"