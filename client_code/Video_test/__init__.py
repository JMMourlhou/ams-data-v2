from ._anvil_designer import Video_testTemplate
from anvil import *

class Video_test(Video_testTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

        # /mnt/ssd-prog/home/jmm/AMS_data/medias/videos/Essai1.mp4
        # https://videos.jmweb34.net  est le sous domaine configuré dans cloudflare

        self.video_player_1.video_url = (
            "https://videos.jmweb34.net/Essai1_stream.mp4"

        )

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 
