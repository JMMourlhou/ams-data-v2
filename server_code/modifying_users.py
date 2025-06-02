import anvil.email
# CREATION 
import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
@anvil.tables.in_transaction
def modify_users(user_to_be_modified,
                     nom,
                     prenom,
                     photo,
                     ville_naissance,
                     cp_naissance,
                     date_naissance,
                     pays_naissance,
                     rue,
                     ville,
                     cp,
                     tel,
                     mail2,
                     accept_storage,
                     comments
                ):
    # finding the user's row 
    row=anvil.users.get_user(user_to_be_modified)
    
    if not row:
        raise Exception("Erreur: stagiaire non trouvé (mail modifié?) !")
        return False
    else:           
        row.update(nom=nom,
                   prenom=prenom,
                   photo = photo,
                   ville_naissance = ville_naissance,
                   code_postal_naissance = cp_naissance,
                   date_naissance = date_naissance,
                   pays_naissance = pays_naissance,
                   adresse_rue = rue,
                   adresse_ville = ville,
                   adresse_code_postal = cp,
                   tel = tel,
                   email2 = mail2,
                   accept_data = accept_storage,
                   commentaires = comments
                            )
        return True


#=======================================================================================
# In qcm process, maj d'un qcm, l'utilisateur demande un test en visu
@anvil.server.callable
@anvil.tables.in_transaction
def modify_users_temp2(user_to_be_modified, temp2):
    # finding the user's row 
    row=anvil.users.get_user(user_to_be_modified)
    
    if not row:
        raise Exception("Erreur: stagiaire non trouvé (mail modifié?) !")
        return False
    else:           
        row.update(temp2=temp2)
        return True