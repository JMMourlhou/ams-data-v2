from ._anvil_designer import HTML_partTemplate
from anvil import *

import anvil.js

class HTML_part(HTML_partTemplate):
    def __init__(self, html_text="", **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.border = "1px solid #33a1b8"

