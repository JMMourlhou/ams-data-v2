import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# ------------------------------------------------------------------------------------------- MAJ Table Global_variables   (Form Global_Variables_MAJ_table)
#Création d'une nouvelle variable globale
@anvil.server.callable 
def add_global_variables( name,     # row codes_stage concernée
                        value,
                        commentaires):
    
    new_row=app_tables.global_variables.add_row(
                                            name=name,     
                                            value=value,
                                            Commentaires=commentaires
                                            )
    row = app_tables.global_variables.search(name=new_row['name'])
    if len(row)>0:
        valid=True
    else:
        valid=False
    return valid

    
# ==========================================================================================
#Effact d'une variable globale existante 
@anvil.server.callable 
def del_var_globale(var_globale_row):   # stage_num: num de stage en txt
    result = False
    if var_globale_row:
        var_globale_row.delete()
        result = True
    return result


# ==========================================================================================
@anvil.server.callable           #modif d'un type de stage 
def modif_var_globale(row_code,    # row type de stage
                    name,
                    value,
                    commentaires
                    ):  
    
    valid=False
    row_code.update(
                    name=name,     
                    value=value,
                    Commentaires=commentaires
                    )
    valid=True
    
    return valid
    