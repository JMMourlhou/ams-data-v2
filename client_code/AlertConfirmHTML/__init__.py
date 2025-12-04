from ._anvil_designer import AlertConfirmHTMLTemplate
from anvil import *

class AlertConfirmHTML(AlertConfirmHTMLTemplate):

    def __init__(
        self,
        titre="Confirmation",
        contenu="",
        large=False,
        boutons=[("Oui", True), ("Non", False)],
        style="info",
        **properties
    ):
        self.init_components(**properties)

        self.role = style + "-alert"
        self.rt.content = contenu

        # Création des boutons
        self.button_panel.clear()
        for label, value in boutons:
            b = Button(text=label)
            b.set_event_handler("click", lambda v=value, **e: self.send_response(v))
            self.button_panel.add_component(b)

        # AFFICHAGE DE L’ALERTE
        self.result = alert(
            title=titre,
            content=self,
            large=large,
            dismissible=False,
            buttons=[]     # empêche l'ajout du bouton OK auto
        )

    # SEULE manière autorisée de fermer une alert() depuis une Form
    def send_response(self, value):
        self.raise_event("x-close-alert", value=value)

    @staticmethod
    def ask(titre, contenu, boutons, style="info", large=True):
        form = AlertConfirmHTML(
            titre=titre,
            contenu=contenu,
            boutons=boutons,
            style=style,
            large=large
        )
        return form.result
