from ._anvil_designer import Box_inputTemplate
from anvil import *

class Box_input(Box_inputTemplate):
    def __init__(self, question, drop_down_place_holder=None, drop_down_rows=None, reponse=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()
        self.row = None
        
        if question is not None:
            self.question.text = question
        if reponse is not None:
            self.reponse.visible = True
            self.reponse.placeholder = reponse
        if drop_down_place_holder is not None:
            self.drop_down.visible = True
            self.drop_down.placeholder = drop_down_place_holder
        if drop_down_rows is not None:
            # Initialisation Drop down
            self.drop_down.items = drop_down_rows   # liste []

    def drop_down_change(self, **event_args):
        """This method is called when an item is selected"""
        self.row = self.drop_down.selected_value
        self.button_ok.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.remove_from_parent()

    def button_ok_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.reponse.visible is True:
            open_form(self.f, self.reponse.text)
        else:
            open_form(self.f, self.row)
        
     
