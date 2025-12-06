from ._anvil_designer import AlertHTMLTemplate
from anvil import *

# style "info", "error", "success"
class AlertHTML(AlertHTMLTemplate):
    def __init__(self, titre="Information", contenu="", large=False, style="info", **properties):
        self.init_components(**properties)

        # On applique la couleur selon le style choisi
        self._apply_style(style)

        # Injection du contenu HTML
        self.rt.content = contenu

        # Affichage dans une alert()
        alert(
            title=titre,
            content=self,
            large=large,
            buttons=["OK"]
        )

    # ------------------------------
    # Méthodes de styles
    # ------------------------------
    def _apply_style(self, style):
        if style == "error":
            self.role = "error-alert"
        elif style == "success":
            self.role = "success-alert"
        else:
            self.role = "info-alert"

    # -------------------
    # Méthodes statiques 
    # ------------------
    @staticmethod
    def error(titre, contenu, large=True):
        return AlertHTML(titre=titre, contenu=contenu, large=large, style="error")

    @staticmethod
    def info(titre, contenu, large=True):
        return AlertHTML(titre=titre, contenu=contenu, large=large, style="info")

    @staticmethod
    def success(titre, contenu, large=True):
        return AlertHTML(titre=titre, contenu=contenu, large=large, style="success")
