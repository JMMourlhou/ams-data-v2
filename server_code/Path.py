import anvil.email

import anvil.files
from anvil.files import data_files
import anvil.server
import pathlib

@anvil.server.callable           #extraction des infos d'un file 
def path_infos(file):
    path = pathlib.Path(file)
    print("Parent:", path.parent)
    print("Filename:", path.name)
    print("Extension:", path.suffix)
    return str(path.parent), str(path.name), str(path.suffix)