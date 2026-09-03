from ._anvil_designer import z_check_up_mpTemplate
import anvil
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *

class z_check_up_mp(z_check_up_mpTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        


    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        temporary_password = self.text_box_temporary_password.text
        if len(temporary_password) == 0:
            alert("Entrez un Mp")
            self.text_box_temporary_password.focus()
            return
        self.task = anvil.server.call("users_with_temporary_password", temporary_password)
        print("Fin de BG task")

        
