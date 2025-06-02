import anvil.email
import anvil.tables as tables
#import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil.pdf import PDFRenderer
"""
         Génération du doc pdf après avoir visualiser l'image jpg correspondante à 'Pre_Visu_img_Pdf_Generation'

    quality :
    "original": All images will be embedded at original resolution. Output file can be very large.
    "screen": Low-resolution output similar to the Acrobat Distiller “Screen Optimized” setting.
    "printer": Output similar to the Acrobat Distiller “Print Optimized” setting.
    "prepress": Output similar to Acrobat Distiller “Prepress Optimized” setting.
 ** "default": Output intended to be useful across a wide variety of uses, possibly at the expense of a larger output file.
    """
# Ce module n'est pas utilisé
@anvil.server.callable
def generate_pdf_from_jpg(file, file_name, stage_num, email, item_requis, pr_requis_row):
    pdf_object = PDFRenderer(page_size ='A4',
                            filename = f"{file_name}.pdf",
                            landscape = False,
                            margins = {'top': 0.3, 'bottom': 0.1, 'left': 0.2, 'right': 0.2},  #  cm
                            scale = 1.0,                                                       
                            quality = "default"       # ok pdf 3300 ko --> pdf 368 ko
                            ).render_form('Pre_Visu_img_Pdf_Generation',file, file_name)
    """                
    # save mediaobject in table pre requi du stage si: doc PDF pas encore existant en table (jpg chargé à l'origine) 
    #                                                  ou si le nom du doc pdf pas encore formatté (pdf chargé en 1er)
    
    media = pr_requis_row['pdf_doc1']   #j'extrai le nom du doc pdf ds la table
    if media != None:
        name_media = media.name[0:3]   
        try:
            test_if_integer = int(media) # pas d'erreur donc doc pdf a un nom déjà formatté, je ne sauve pas.
        except:      # si 3 1eres lettres ne sont pas numériques: c'est le doc pdf chargé au départ, et nom d'origine en table, je sauve
            pr_requis_row.update(pdf_doc1 = pdf_object)
    else:  # si pas de doc pdf pour ce doc, je sauve
        pr_requis_row.update(pdf_doc1 = pdf_object)
    """
    return pdf_object   # pour download 






