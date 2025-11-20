from ._anvil_designer import HTML_partTemplate
from anvil import *

import anvil.js

class HTML_part(HTML_partTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
