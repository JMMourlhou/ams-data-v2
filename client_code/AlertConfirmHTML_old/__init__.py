from ._anvil_designer import AlertConfirmHTML_oldTemplate
from anvil import *
import anvil.js


class AlertConfirmHTML_old(AlertConfirmHTML_oldTemplate):
    def __init__(
        self,
        titre="Confirmation",
        contenu="",
        style="info",      # "info", "error", "success"
        large=False,
        **properties
    ):
        self.init_components(**properties)
        print("TYPE:", type(self.button_panel))
        
        # Style principal : .anvil-role-info-alert / .anvil-role-error-alert / .anvil-role-success-alert
        self.role = style + "-alert"

        # Contenu HTML (restricted_html)
        self.rt.format = "restricted_html"
        self.rt.content = contenu

        # ------------------------------------------------------------------
        # 1) Injecter les boutons en HTML dans le HtmlPanel
        # ------------------------------------------------------------------
        self.button_panel.html = """
        <div class="alert-buttons">
          <button id="alert-btn-oui" type="button">Oui</button>
          <button id="alert-btn-non" type="button">Non</button>
        </div>
        """

        # ------------------------------------------------------------------
        # 2) Afficher l'alerte (sans bouton OK par défaut)
        # ------------------------------------------------------------------
        self.result = alert(
            title=titre,
            content=self,
            large=large,
            dismissible=False,
            buttons=[]
        )

        # ------------------------------------------------------------------
        # 3) Lier les clics JS -> Python + focus par défaut
        # ------------------------------------------------------------------
        def bind_events_and_focus():
            doc = anvil.js.window.document

            btn_oui = doc.getElementById("alert-btn-oui")
            btn_non = doc.getElementById("alert-btn-non")

            if btn_oui is not None:
                def on_oui(ev):
                    self._choose(True)
                btn_oui.addEventListener("click", on_oui)
                btn_oui.focus()

            if btn_non is not None:
                def on_non(ev):
                    self._choose(False)
                btn_non.addEventListener("click", on_non)

        # Petit délai pour laisser Anvil rendre le contenu de l'alert
        anvil.js.window.setTimeout(bind_events_and_focus, 50)

    # ------------------------------------------------------------------
    # Fermeture propre de l'alerte : renvoie True / False à alert(...)
    # ------------------------------------------------------------------
    def _choose(self, value):
        self.raise_event("x-close-alert", value=value)

    # ------------------------------------------------------------------
    # Méthode statique utilitaire
    # ------------------------------------------------------------------
    @staticmethod
    def ask(titre, contenu="", style="info", large=False):
        form = AlertConfirmHTML(
            titre=titre,
            contenu=contenu,
            style=style,
            large=large,
        )
        return form.result
