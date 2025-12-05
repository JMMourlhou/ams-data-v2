from ._anvil_designer import Form1Template
from anvil import *

class AlertConfirmHTML2(AlertConfirmHTML2Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        print("TEMPLATE:", self.__class__.__bases__)