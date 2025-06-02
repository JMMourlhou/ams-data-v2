import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server

# sauve le param type de formulaire de suivi  ds table temp
@anvil.server.callable
def temp_type_suivi(type_suivi):
    result = False
    temp_row = app_tables.temp.search()[0]
    temp_row.update(type_suivi=type_suivi)