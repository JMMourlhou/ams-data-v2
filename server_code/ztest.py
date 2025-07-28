import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_cpt_columns():
    return [col["name"] for col in app_tables.cpt_stages._table.columns]
