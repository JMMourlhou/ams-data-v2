import anvil.email

import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


from . import French_zone_server_side
import anvil.pdf
from anvil.pdf import PDFRenderer

@anvil.server.background_task
def create_list_pdf(num_stage, intitule):
    """
    quality :
    "original": All images will be embedded at original resolution. Output file can be very large.
    "screen": Low-resolution output similar to the Acrobat Distiller “Screen Optimized” setting.
    "printer": Output similar to the Acrobat Distiller “Print Optimized” setting.
    "prepress": Output similar to Acrobat Distiller “Prepress Optimized” setting.
    "default": Output intended to be useful across a wide variety of uses, possibly at the expense of a larger output file.
    """
    media_object = PDFRenderer(page_size ='A4',
                               filename = f"{intitule}/{num_stage}.pdf",
                               landscape = False,
                               margins = {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0},  # en cm
                               scale = 1.0,
                               quality =  "default"
                              ).render_form('Visu_liste_1_stage',num_stage, intitule, True)
    
    " sauvegarde du media_object ds la table "
    #lecture du fichier stages sur le num de stage
    stage_row = app_tables.stages.get(numero=int(num_stage))
    if not stage_row:   
        print("stage non trouvé à partir de num_stage ds server module: Stagiaires_list_pdf")
    else:
        # sauvegarde de la liste pdf ds le stage_row
        print("sov")
        stage_row.update(list_media = media_object,
                        list_time = French_zone_server_side.time_french_zone()
                        ) 


@anvil.server.callable
def run_bg_task_stage_list(num_stage, intitule):
    task = anvil.server.launch_background_task('create_list_pdf',num_stage, intitule)
    return task
        

