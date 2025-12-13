from ._anvil_designer import Video_PlayerTemplate
from anvil import *
import anvil.js


class Video_Player(Video_PlayerTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        # Accès DOM du Custom HTML
        self._root = self.html_video.dom_node

        # Branche event "ended" -> event Anvil
        v = anvil.js.window._vp_get(self._root)
        v.onended = lambda *args: self.raise_event("x-ended")

        # Si la propriété est définie → on charge la vidéo
        if getattr(self, "video_url", ""):
            self._apply_video_url(self.video_url)

    # ---------- interne ----------
    def _apply_video_url(self, url: str):
        """Applique l'URL au lecteur (interne)."""
        anvil.js.window._vp_set_src(self._root, url or "")

    # --------- API publique ---------
    def set_video_url(self, url: str):
        """Optionnel : permet de changer la vidéo par code."""
        self.video_url = url   # garde la property en source de vérité

    def play(self):
        v = anvil.js.window._vp_get(self._root)
        v.play()

    def pause(self):
        v = anvil.js.window._vp_get(self._root)
        v.pause()

    def stop(self):
        v = anvil.js.window._vp_get(self._root)
        v.pause()
        v.currentTime = 0

    def set_time(self, seconds: float):
        v = anvil.js.window._vp_get(self._root)
        v.currentTime = float(seconds)

    def current_time(self) -> float:
        v = anvil.js.window._vp_get(self._root)
        return float(v.currentTime or 0)

    def duration(self) -> float:
        v = anvil.js.window._vp_get(self._root)
        return float(v.duration or 0)

    # --------- property change handler ---------
    def video_url_changed(self, **event_args):
        # Cette méthode est appelée AUTOMATIQUEMENT par Anvil
        # quand la property `video_url` change (Designer ou code).
        self._apply_video_url(self.video_url)
