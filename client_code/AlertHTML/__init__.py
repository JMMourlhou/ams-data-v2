from ._anvil_designer import AlertHTMLTemplate
from anvil import *


class AlertHTML(AlertHTMLTemplate):
    def __init__(self, contenu="", style="info", **properties):
        self.init_components(**properties)

        # Application du style
        self._apply_style(style)

        # Contenu HTML
        self.rt.content = contenu


    # ------------------------------------------------------------------------------------------
    # Application du style de l'alerte
    # ------------------------------------------------------------------------------------------
    def _apply_style(self, style):
        if style == "error":
            self.role = "error-alert"
        elif style == "success":
            self.role = "success-alert"
        else:
            self.role = "info-alert"


    # ------------------------------------------------------------------------------------------
    # Affichage commun des alertes
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def _show(titre, contenu, large, style):
        contenu_alert = AlertHTML(contenu=contenu, style=style)

        return alert(
            title=titre,
            content=contenu_alert,
            large=large,
            dismissible=True,
            buttons=[("OK", True)]
        )


    # ------------------------------------------------------------------------------------------
    # Alerte erreur
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def error(titre, contenu, large=True):
        return AlertHTML._show(titre, contenu, large, "error")


    # ------------------------------------------------------------------------------------------
    # Alerte information
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def info(titre, contenu, large=True):
        return AlertHTML._show(titre, contenu, large, "info")


    # ------------------------------------------------------------------------------------------
    # Alerte succès
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def success(titre, contenu, large=True):
        return AlertHTML._show(titre, contenu, large, "success")