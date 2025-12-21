from ._anvil_designer import Video_testTemplate
from anvil import *


class Video_test(Video_testTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.video_player_1.load(
            url="https://jmweb34.net/videos/Essai1_stream.mp4",
            autoplay=True,
            muted=False,
            controls=True,
            v_width="100%",    # "50%"
            v_height="100%",   # ou en px : "360px"
            allow_download=False
        )
        self.video_player_1.set_event_handler(
            "x-video-ended",
            self.video_finished
        )

    def video_finished(self, **e):
        # ✅ Validation QCM
        #self.button_valider.enabled = True
        n = Notification("Fin de la video", timeout=2)   # par défaut 2 secondes
        n.show()
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 
