import anvil.email

import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
@anvil.tables.in_transaction
def modify_users_after_trombi(mel,
                     mail_modif,                
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
                     comments,
                     role
                ):
    # finding the stagiaire's row 
    
    row = app_tables.users.get(email=mel)
    
    try:
        row.update(email=mail_modif,
                nom=nom,
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
                commentaires = comments,
                role = role
                            )
        return True
    except Exception as e:
        print(f"Erreur en MAJ user: {e}")
        return e
        

# Appelé des paramètres, modif table users, colonnes mail confirmé   et     compte enabled
@anvil.server.callable
def modify_users_from_parameters(user_row, confirmed, enabled, nb_pw_failure):  
    print(f"confirmed: {confirmed}")
    print(f"enabled: {enabled}")
    print(f"nb_pw_failures: {nb_pw_failure}")
    
    result = False
    user_row.update(confirmed_email=confirmed,
                    enabled=enabled,
                    n_password_failures=nb_pw_failure)
    result = True
    return result
                    