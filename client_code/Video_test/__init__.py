from ._anvil_designer import Video_testTemplate
from anvil import *



class Video_test(Video_testTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        
        # /mnt/ssd-prog/home/jmm/AMS_data/medias/videos/Essai1.mp4
        self.video_player_1.video_url = "https://www.jmweb34.net/videos/qcm_002.mp4"
        