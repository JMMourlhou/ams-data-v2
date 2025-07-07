import anvil.files
from anvil.files import data_files
import anvil.server
import anvil.pdf
from anvil.pdf import PDFRenderer

@anvil.server.callable
def test_pdf():
    media_object = PDFRenderer(page_size ='A4',
                            filename = "test.pdf",
                            landscape = False,
                            margins = {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0},  # en cm
                            scale = 1.0,
                            quality =  "default"
                            ).render_form('TEST_PDF')
    return media_object
