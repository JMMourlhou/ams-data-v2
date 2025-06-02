import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# accès à une var globale précise (en donnant son nom coté client)
@anvil.server.callable
def get_variable_value(variable_name):
    # 'variable' nom de la variable globale ds table 'global_variables')
    # 'value' contenu de ma variable globale.
    row = app_tables.global_variables.get(name=variable_name)
    if row:
        # Return the value associated with the variable name
        return row['value']
    else:
        # Handle the case where the variable does not exist
        return None


# Pour avoir en mémoire toutes les variables sous forme de dict
@anvil.server.callable
def get_variable_names():
    liste = app_tables.global_variables.search(q.fetch_only("name","value"))
    dict = {}
    for var_glob in liste:
        dict[var_glob['name']]=var_glob['value']
    print(dict)
    return(dict)
        

"""
# pour mettre à jour éventuellement les variables par programme
@anvil.server.callable
def set_variable_value(variable_name, value):
    row = app_tables.global_variables.get(name=variable_name)
    if row:
        # If the variable already exists, update its value
        row['value'] = value
    else:
        # If the variable does not exist, add a new row to the table
        app_tables.global_variables.add_row(name=variable_name, value=value)

    return value
"""