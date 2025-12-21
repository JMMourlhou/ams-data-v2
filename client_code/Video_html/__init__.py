from ._anvil_designer import Video_htmlTemplate
from anvil import *
import anvil.js

class Video_html(Video_htmlTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        # si la propriété est déjà définie
        if self.video_url:
            self._load_video(self.video_url)

    def _load_video(self, url):
        print("VIDEO_HTML load URL =", url)

        container = anvil.js.get_dom_node(self)
        video = container.querySelector("#video_player")
    
        print("VIDEO element =", video)
    
        video.src = url

    def video_url_changed(self, **event_args):
        if self.video_url:
            self._load_video(self.video_url)
