from ._anvil_designer import Video_PlayerTemplate
from anvil import *

class Video_Player(Video_PlayerTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._sync()

    def _sync(self):
        # Réinjecte l’URL ET force le re-render du HTML
        self.html_video_1.video_url = self.video_url
        self.html_video_1.visible = False
        self.html_video_1.visible = True

    def video_url_changed(self, **event_args):
        self._sync()
