from ._anvil_designer import Video_PlayerTemplate
from anvil import *
import anvil.js


class Video_Player(Video_PlayerTemplate):

    def __init__(self, **properties):
        self.init_components(**properties)

        video_url = "https://media.jmweb34.net/Essai1_stream.mp4"

        # 1️⃣ Récupère le noeud DOM racine du composant HTML
        root = anvil.js.get_dom_node(self.video_html_1)

        # 2️⃣ Récupère LE BON conteneur (<div id="video-container">)
        video_container = root.querySelector("#video-container")

        # 3️⃣ Injecte la balise <video> AU BON ENDROIT
        video_container.innerHTML = f"""
            <h3 style="color:red;">Vidéo test</h3>
            <video controls preload="metadata" style="width:100%; max-height:360px;">
                <source src="{video_url}" type="video/mp4">
                Votre navigateur ne supporte pas la vidéo.
            </video>
        """

