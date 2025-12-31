from ._anvil_designer import Video_Player_sauvegardeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js


class Video_Player_sauvegarde(Video_Player_sauvegardeTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def _ensure_css(self):
        # Ajoute le style UNE SEULE FOIS dans <head>
        doc = anvil.js.window.document
        if doc.getElementById("video-player-css"):
            return

        style = doc.createElement("style")
        style.id = "video-player-css"
        style.textContent = """
        .video-player-blue{
            border: 2px solid #347eff;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(52,126,255,0.35);
            background: black;
        }
        """
        doc.head.appendChild(style)

    def load(
        self,
        url: str,
        autoplay=False,
        muted=False,
        controls=True,
        v_width="100%",
        v_height="360px",
        allow_download=False,
    ):
        alert(url)
        self._ensure_css()

        root = anvil.js.get_dom_node(self.video_html_1)
        container = root.querySelector("#video-container")
        if not container:
            raise RuntimeError("Conteneur #video-container introuvable")

        autoplay_attr = "autoplay" if autoplay else ""
        muted_attr = "muted" if muted else ""
        controls_attr = "controls" if controls else ""
        controlslist_attr = (
            "" if allow_download else 'controlslist="nodownload noplaybackrate"'
        )

        container.innerHTML = f"""
            <video
                id="qcm-video"
                class="video-player-blue"
                {autoplay_attr}
                {muted_attr}
                {controls_attr}
                {controlslist_attr}
                disablepictureinpicture
                playsinline
                preload="metadata"
                style="
                    width:{v_width};
                    height:{v_height};
                    display:block;
                    margin:auto;
                "
            >
                <source src="{url}" type="video/mp4">
            </video>
        """

        video = container.querySelector("#qcm-video")
        video.addEventListener("contextmenu", lambda e: e.preventDefault())

        def on_video_ended(evt):
            self.raise_event("x-video-ended")

        video.addEventListener("ended", on_video_ended)


