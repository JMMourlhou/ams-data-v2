from ._anvil_designer import QCM_visu_modif_htmlTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class QCM_visu_modif_html(QCM_visu_modif_htmlTemplate):
    def __init__(self, liste, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

        # Pour les lignes QCM déjà crée du repeating panel
        # liste = list(app_tables.qcm.search())
        self.repeating_panel_1.items = liste
        nb_questions = len(liste)
        self.nb_questions = nb_questions

    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        # self.image_photo.source = file
        thumb_pic = anvil.image.generate_thumbnail(file, 320)
        self.image_photo.source = thumb_pic
        self.button_validation.visible = True

    def repeating_panel_1_show(self, **event_args):
        """This method is called when the RepeatingPanel is shown on the screen"""
        self.repeating_panel_1.tag = "repeat_panel"
