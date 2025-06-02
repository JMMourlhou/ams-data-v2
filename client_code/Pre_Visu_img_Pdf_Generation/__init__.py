import anvil.server
from ._anvil_designer import Pre_Visu_img_Pdf_GenerationTemplate


class Pre_Visu_img_Pdf_Generation(Pre_Visu_img_Pdf_GenerationTemplate):
    def __init__(self, file, file_name, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.image_1.source = file
        self.label_1.text = file_name

   
