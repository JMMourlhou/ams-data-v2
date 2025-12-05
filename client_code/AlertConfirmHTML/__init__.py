from ._anvil_designer import AlertConfirmHTMLTemplate
from anvil import *

class AlertConfirmHTML(AlertConfirmHTMLTemplate):

    def __init__(self, **properties):
        self.init_components(**properties)
        # (code désactivé temporairement)
