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

    # Effacement des enregistrements liés au user ds tables com com_sum qcm_result stage_satisf stage_suivi
    # com
    list = app_tables.com.search(user=row)
    if list:
        for r in list:
            r.delete()
            
    # com_sum
    list = app_tables.com_sum.search(user=row)
    if list:
        for r in list:
            r.delete()

    # qcm_result
    list = app_tables.qcm_result.search(user_qcm=row)
    if list:
        for r in list:
            r.delete()

    # stage_satisf
    list = app_tables.stage_satisf.search(user_email=row)
    if list:
        for r in list:
            r.delete()

    # stage_satisf
    list = app_tables.stage_suivi.search(user_email=row)
    if list:
        for r in list:
            r.delete()
            
    # EFFACEMENT DE LA TABLE USERS        
    row.delete()
    # Vérification
    row1 = app_tables.users.get(email=sov_mail_pour_verif)
    if not row1:
        msg = "Effacement complet effectué !"
    return msg
    