
import anvil.files
from anvil.files import data_files

import anvil.tables as tables

from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def modif_file_table(file, row):
    result = False
    row.update()
    return result
