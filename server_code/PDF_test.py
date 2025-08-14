import anvil.server
import anvil.pdf
from anvil.tables import app_tables

@anvil.server.background_task
def generate_test_pdf():
    # rend un Form par son nom (utile si tu as un Form dédié au PDF)
    media=anvil.pdf.render_form("TestPagebreak")
    
    #lecture du fichier stages sur le num de stage
    stage_row = app_tables.stages.get(numero=1000)
    if not stage_row:   
        print("Stage row not found")
    else:
        # saving the trombinoscope stage media object
        stage_row.update(trombi_media = media)
        
@anvil.server.callable
def test_pdf():
    task = anvil.server.launch_background_task('generate_test_pdf')
    return task