from ._anvil_designer import Video_PlayerTemplate
from anvil import *
import anvil.js

class Video_Player(Video_PlayerTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        # Accès au DOM du Custom HTML
        self._root = self.html_video.dom_node

        # Si une URL est déjà définie, on charge la vidéo
        if self.video_url:
            self._apply_video_url(self.video_url)

    def _apply_video_url(self, url):
        anvil.js.window._vp_set_src(self._root, url or "")

    # Appelé automatiquement par Anvil quand video_url change
    def video_url_changed(self, **event_args):
        self._apply_video_url(self.video_url)
