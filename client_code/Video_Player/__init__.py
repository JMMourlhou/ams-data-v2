from ._anvil_designer import Video_PlayerTemplate
from anvil import *
import anvil.js

class Video_Player(Video_PlayerTemplate):

    def __init__(self, **properties):
        self.init_components(**properties)

    def _ensure_css(self):
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

    # ================================
    # LOAD VIA URL (Pi5 ou Media URL)
    # ================================
    def load(self, url: str, autoplay=False, muted=False, controls=True,
             v_width="100%", v_height="360px", allow_download=False):

        self._ensure_css()

        root = anvil.js.get_dom_node(self.video_html_1)
        container = root.querySelector("#video-container")
        if not container:
            raise RuntimeError("Conteneur #video-container introuvable")

        autoplay_attr = "autoplay" if autoplay else ""
        muted_attr = "muted" if muted else ""
        controls_attr = "controls" if controls else ""
        controlslist_attr = "" if allow_download else 'controlslist="nodownload noplaybackrate"'

        container.innerHTML = f"""
            <video
                id="qcm-video"
                class="video-player-blue"
                src="{url}"
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
            ></video>
        """

        video = container.querySelector("#qcm-video")
        video.load()

        video.addEventListener("contextmenu", lambda e: e.preventDefault())

        def on_video_ended(evt):
            self.raise_event("x-video-ended")

        video.addEventListener("ended", on_video_ended)

    # ================================
    # CLEAR
    # ================================
    def clear(self):
        root = anvil.js.get_dom_node(self.video_html_1)
        container = root.querySelector("#video-container")
        if container:
            container.innerHTML = ""

    # ================================
    # MODE MEDIA ANVIL (temp video ds asset)
    # ================================
    def load_media(self, media: Media, **kwargs):
        if not media:
            self.clear()
            return

        # url = media.get_url()
        url = media
        self.load(url, **kwargs)
