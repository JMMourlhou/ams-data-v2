from ._anvil_designer import AlertConfirmHTMLTemplate
from anvil import *

class AlertConfirmHTML(AlertConfirmHTMLTemplate):

    def __init__(
        self,
        titre="Confirmation",
        contenu="",
        style="info",     # "info", "error", "success"
        large=False,
        **properties
    ):
        self.init_components(**properties)

        # Appliquer le style principal: .anvil-role-info-alert / error / success
        self.role = style + "-alert"

        # Contenu HTML
        self.rt.format = "restricted_html"
        self.rt.content = contenu

        # Lier les boutons
        self.button_yes.set_event_handler("click", lambda **e: self._choose(True))
        self.button_no.set_event_handler("click", lambda **e: self._choose(False))

        # Afficher l'alerte
        self.result = alert(
            title=titre,
            content=self,
            large=large,
            dismissible=False,
            buttons=[]        # pas de bouton OK automatique
        )

        # Focus par défaut sur "Oui"
        self.call_later(0.05, self.btn_oui.focus)

    def _choose(self, value):
        # Ferme l'alert et renvoie value comme résultat
        self.raise_event("x-close-alert", value=value)

    @staticmethod
    def ask(titre, contenu, style="info", large=False):
        form = AlertConfirmHTML(
            titre=titre,
            contenu=contenu,
            style=style,
            large=large,
        )
        return form.result