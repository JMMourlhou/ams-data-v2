from ._anvil_designer import QrCode_GeneratorTemplate
from anvil import *
import anvil.server

# Génération de QR code à partir du texte saisi pui téléchrgt en pdf
class QrCode_Generator(QrCode_GeneratorTemplate):
    def __init__(self, txt="", **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.image_1.visible = False
        self.button_pdf.visible = False
        # Any code you write here will run before the form opens.
        if txt != "":
            self.column_panel_1.visible = False
            self.text_box_1.text = txt
            self.text_box_1_pressed_enter()
    
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def text_box_1_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        text = self.text_box_1.text
        print("code",text)
        media=anvil.server.call('mk_qr_code',text)
        self.image_1.source=media
        self.image_1.visible = True
        self.button_pdf.visible = True

    def button_pdf_click(self, **event_args):
        """This method is called when the button is clicked"""
        txt = self.text_box_1.text
        pdf = anvil.server.call("generate_pdf",txt, file_name="document")
        if pdf:
            anvil.media.download(pdf)
            alert("QR code téléchargé !")
        else:
            alert("Pdf du QR code non généré")
