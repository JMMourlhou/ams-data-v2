from ._anvil_designer import AlertHTMLTemplate
from anvil import *


class AlertHTML(AlertHTMLTemplate):

    @staticmethod
    def _show(titre, contenu, large, style):
        contenu_alert = RichText()
        contenu_alert.format = "restricted_html"
        contenu_alert.content = contenu

        if style == "error":
            contenu_alert.role = "error-alert"
        elif style == "success":
            contenu_alert.role = "success-alert"
        else:
            contenu_alert.role = "info-alert"

        return alert(title=titre, content=contenu_alert, large=large, dismissible=True, buttons=[("OK", True)])

    @staticmethod
    def error(titre, contenu, large=True):
        return AlertHTML._show(titre, contenu, large, "error")

    @staticmethod
    def info(titre, contenu, large=True):
        return AlertHTML._show(titre, contenu, large, "info")

    @staticmethod
    def success(titre, contenu, large=True):
        return AlertHTML._show(titre, contenu, large, "success")