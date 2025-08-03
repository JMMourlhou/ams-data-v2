import anvil.files
from anvil.files import data_files
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def modif_file_table(file, row, name, commentaires, modif_checked, del_checked):
    msg = "Modification Effectuée !"
    result = False
    try:
        row.update(file=file,
                path=name,
                commentaires=commentaires,
                modifiable=modif_checked,
                annulable=del_checked)
    
        result = True
    except Exception as e:
        msg = e
    return result, msg

@anvil.server.callable
def del_file_table(row):
    msg = "Effacement Effectué !"
    result = False
    try:
        row.delete()
        result = True
    except Exception as e:
        msg = e
    return result, msg

@anvil.server.callable
def add_file_table(file, name, commentaires, modif_checked, del_checked):
    msg = "Ajout Effectué !"
    result = False
    try:
        app_tables.files.add_row(
                                file=file,
                                path=name,
                                commentaires=commentaires,
                                modifiable=modif_checked,
                                annulable=del_checked
                                )
        result = True
    except Exception as e:
        msg = e
    return result, msg