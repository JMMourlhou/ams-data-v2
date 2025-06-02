from ._anvil_designer import SignatureTemplate
from anvil import *
import anvil.server

import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables

class Signature(SignatureTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run when the form opens.
        self.pen_down = False
        self.lastx = self.lasty = 0
    
    def canvas_1_mouse_leave (self, x, y, **event_args):
        # This method is called when the mouse cursor leaves this component
        self.pen_down = False
    
    def canvas_1_mouse_down (self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        self.pen_down = True
        self.lastx = x # The (x,y) coordinates are calculated with reference to the top-left corner of the Canvas.
        self.lasty = y
    
    def canvas_1_mouse_move (self, x, y, **event_args):
        # This method is called when the mouse cursor moves over this component
        if self.pen_down:
            self.canvas_1.begin_path() # Tells the canvas that you are about to start drawing a shape.
            self.canvas_1.move_to(self.lastx, self.lasty) # Move to position (x, y) without drawing anything, ready to start the next edge of the current shape. The (x,y) coordinates are calculated with reference to the top-left corner of the Canvas.
            self.canvas_1.line_to(x, y) # Draw a line to position (x, y). The (x,y) coordinates are calculated with reference to the top-left corner of the Canvas.
            self.canvas_1.stroke()  # Draws the outline of the shape you have defined in the current stroke_style.
            self.lastx = x
            self.lasty = y
    
    def canvas_1_mouse_up (self, x, y, button, **event_args):
        # This method is called when a mouse button is released on this component
        self.pen_down = False
    
    def form_show (self, **event_args):
        # This method is called when the column panel is shown on the screen
        self.canvas_1.line_width = 5
        self.canvas_1.line_cap = "round"   # The style of line ends. 
        self.canvas_1.stroke_style = "#FFFFFF" # The colour of lines drawn on the canvas.   "#RRGGBB" ou "rgba(255,0,0,1)"
        
    def get_image(self):
        return self.canvas_1.get_image()  # get_image() : get the contents of the canvas as a Media object
    
    def clear(self):
        # get_width()  get_height()  : Returns the width and height of the canvas, in pixels
        self.canvas_1.clear_rect(0, 0, self.canvas_1.get_width(), self.canvas_1.get_height()) # Clears a rectangle The (x,y) coordinates are calculated with reference to the top-left corner of the Canvas.

    
    def button_save_click (self, **event_args):
    # This method is called when the button is clicked
        self.column_panel_2.visible = True        # contient l'image générée 
        self.image_1.source = self.get_image()    # get_image() : get the contents of the canvas as a Media object
        self.clear()   # dessine le rectangle à blanc, appel au module d'effact du canvas_1      def clear(self):

    def button_erase_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.clear()  # appel au module d'effact du canvas_1      def clear(self):

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)
