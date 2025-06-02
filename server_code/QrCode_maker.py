import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.server
import qrcode
import qrcode.image.svg
from io import BytesIO
import anvil.media
from anvil.pdf import PDFRenderer


@anvil.server.callable
def mk_qr_code(qr_code_data, **params):
    qr_code_obj = qrcode.make(qr_code_data, 
                              image_factory=qrcode.image.svg.SvgPathImage, 
                              error_correction=qrcode.constants.ERROR_CORRECT_Q,
                              box_size=25, version=2)
    data = BytesIO()
    qr_code_obj.save(data)
    data.seek(0)
    svg_text = data.read()
    
    b = anvil.BlobMedia("image/svg+xml", svg_text, name="qrcode.svg")
    return b


# Génère un pdf d'un fichier
@anvil.server.callable
def generate_pdf(file, file_name="document"):
    pdf_object = PDFRenderer(page_size ='A4',
                            filename = f"{file_name}.pdf",
                            landscape = False,
                            margins = {'top': 0.3, 'bottom': 0.1, 'left': 0.2, 'right': 0.2},  #  cm
                            scale = 1.0,                                                       
                            quality = "default"       # ok pdf 3300 ko --> pdf 368 ko
                            ).render_form('QrCode_Generator',file)
    return pdf_object   # pour download 