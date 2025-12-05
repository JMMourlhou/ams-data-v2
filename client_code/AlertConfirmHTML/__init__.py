from ._anvil_designer import AlertConfirmHTMLTemplate
from anvil import *
import anvil.js

class AlertConfirmHTML(AlertConfirmHTMLTemplate):

    def __init__(
        self,
        titre="Confirmation",
        contenu="",
        style="info",      # "info", "error", "success"
        large=False,
        **properties
    ):
        self.init_components(**properties)

        # Style principal : .anvil-role-info-alert/.error-alert/.success-alert
        self.role = style + "-alert"

        # Contenu HTML
        self.rt.format = "restricted_html"
        self.rt.content = contenu

        # Boutons
        self.btn_oui.set_event_handler("click", lambda **e: self._choose(True))
        self.btn_non.set_event_handler("click", lambda **e: self._choose(False))

        # Affichage de l'alerte
        self.result = alert(
            title=titre,
            content=self,
            large=large,
            dismissible=False,
            buttons=[]
        )

        # Focus sur OUI par défaut
        anvil.js.window.setTimeout(lambda: self.btn_oui.focus(), 50)

    def _choose(self, value):
        self.raise_event("x-close-alert", value=value)

    @staticmethod
    def ask(titre, contenu="", style="info", large=False):
        form = AlertConfirmHTML(
            titre=titre,
            contenu=contenu,
            style=style,
            large=large,
        )
        return form.result
