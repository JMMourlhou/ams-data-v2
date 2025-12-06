from ._anvil_designer import AlertConfirmHTML_copyTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js


class AlertConfirmHTML_copy(AlertConfirmHTML_copyTemplate):
    def __init__(
        self, titre="Confirmation", contenu="", style="info", large=False, **properties
    ):
        self.init_components(**properties)

        # -----------------------------
        # 1) Bloc contenu stylé
        # -----------------------------
        content_block = FlowPanel(role=style + "-alert")
        content_block.add_component(RichText(format="restricted_html", content=contenu))
        self.add_component(content_block, slot="content")

        # -----------------------------
        # 2) Boutons Anvil dans le slot HTML
        # -----------------------------
        buttons_panel = FlowPanel()

        self.btn_oui = Button(text="Oui")
        self.btn_non = Button(text="Non")

        buttons_panel.add_component(self.btn_oui)
        buttons_panel.add_component(self.btn_non)

        self.add_component(buttons_panel, slot="buttons")

        # -----------------------------
        # 3) Gestion des clics
        # -----------------------------
        self.btn_oui.set_event_handler("click", lambda **e: self._choose(True))
        self.btn_non.set_event_handler("click", lambda **e: self._choose(False))

        # -----------------------------
        # 4) SUPPRIMER LE FOCUS AUTO
        # -----------------------------
        import anvil.js

        anvil.js.window.setTimeout(
            lambda: anvil.js.window.document.activeElement.blur(), 50
        )

    # ----------- Focus JS (option 2) -----------
    def _on_show(self, **event_args):
        """Met automatiquement le focus sur le bouton Oui."""
        doc = anvil.js.window.document

        # Sélectionne le premier <button> dans <div class="alert-buttons">
        btn = doc.querySelector(".alert-buttons button")

        if btn:
            btn.focus()

    def _choose(self, value):
        """Ferme l’alerte avec True / False."""
        self.raise_event("x-close-alert", value=value)

    # ----------- Méthode statique pour utilisation simple -----------
    @staticmethod
    def ask(titre="Confirmation", contenu="", style="info", large=False):
        """Renvoie True (oui) ou False (non)."""
        form = AlertConfirmHTML(titre, contenu, style, large)
        return alert(
            title=titre,
            content=form,
            dismissible=False,
            buttons=[],
            large=large,
        )
