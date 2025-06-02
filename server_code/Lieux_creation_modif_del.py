from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import *  #pour les alertes


# ==========================================================================================
#Création d'un nouveau lieu
@anvil.server.callable 
def add_lieu(lieu, adresse, commentaires):
    new_row=app_tables.lieux.add_row(
                              lieu=lieu,
                              adresse=adresse,
                              remarques=commentaires
                             )
                 
    row = app_tables.lieux.search(lieu=new_row['lieu'])
    if len(row)>0:
        valid=True
    else:
        valid=False
    return valid

# ==========================================================================================
@anvil.server.callable           #Del d'un lieu (si pas utilisé en table stage)
def del_lieu(lieu_row, code):
    valid = False
    # del des PR stagiaires existants
    liste = app_tables.stages.search(lieu=lieu_row)
    if len(liste)==0:
        lieu_row.delete()
        valid = True
    
    return valid, len(liste), liste

# ==========================================================================================
@anvil.server.callable           #modif d'un lieu et adresse 
def modif_lieu(lieu_row, adresse, lieu, old_lieu):
    valid = False
    lieu_row.update(adresse = adresse,
                   lieu=lieu)
    valid = True
            
    return valid