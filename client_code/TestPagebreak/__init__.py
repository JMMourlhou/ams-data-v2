from ._anvil_designer import TestPagebreakTemplate
import anvil.server
from ..PageBreak import PageBreak
from anvil import Button, Label, Spacer
from anvil import *

class TestPagebreak(TestPagebreakTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        # --- Section 1 :  rapide à repérer dans le PDF
        self.cp.add_component(Label(text="=== SECTION 1 ===", bold=True, font_size=20))
        for i in range(15):
            self.cp.add_component(Label(text=f"Ligne S1 #{i+1}"))

        # --- Insérer le saut de page
        self.cp.add_component(PageBreak(margin_top=24, border="1px dashed #bbb"))

        # --- Section 2
        self.cp.add_component(Label(text="=== SECTION 2 ===", bold=True, font_size=20))
        for i in range(15):
            self.cp.add_component(Label(text=f"Ligne S2 #{i+1}"))

        # un petit espace à la fin (optionnel)
        self.cp.add_component(Spacer(height=10))

    def btn_pdf_click(self, **event_args):
        # Génère un PDF depuis TOUT le Form (inclut cp + PageBreak)
        anvil.server.call("test_pdf")
        alert("Vérif le stage 1000")

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")
        

