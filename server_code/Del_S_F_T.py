import anvil.email

import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Effacement d'un stagiaire, formateur, tuteur de la table users
@anvil.server.callable
def del_personne(row):  
    sov_mail_pour_verif = row['email']
    msg = "Erreur en effacement"
    row.delete()
    # Vérification
    row1 = app_tables.users.get(email=sov_mail_pour_verif)
    if not row1:
        msg = "Effacement effectué !"
    return msg
    