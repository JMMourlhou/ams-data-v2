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
def add_mode_fi(code_mode_fi, intitule):
    new_row=app_tables.mode_financement.add_row(
                              code_fi=code_mode_fi,
                              intitule_fi=intitule
                             )
                 
    row = app_tables.mode_financement.search(code_fi=new_row['code_fi'])
    if len(row)>0:
        valid=True
    else:
        valid=False
    return valid

# ==========================================================================================
@anvil.server.callable           #Del d'un mode de fi (si pas utilisé en table stagiaire inscrits)
def del_mode_fi(mode_fi_row, code_mode_fi):
    valid = False
    # del des PR stagiaires existants
    liste = app_tables.stagiaires_inscrits.search(financement=mode_fi_row)
    if len(liste)==0:
        mode_fi_row.delete()
        valid = True
    
    return valid, len(liste), liste

# ==========================================================================================
@anvil.server.callable           #modif d'un mode de fi et intitulé
def modif_mode_fi(mode_fi_row, code_fi, intitule_fi, old_mode):
    valid = False
    mode_fi_row.update(code_fi=code_fi,
                        intitule_fi=intitule_fi)
    valid = True

    return valid

# ==========================================================================================
@anvil.server.callable           # modif du mode de financement d'un stagiaire, table stagiaire inscris, appelé par Stage_visu_modif, Template4
def modif_mode_fi_1_stagiaire(stagiaire_row, mode_fi_row):
    try:
        stagiaire_row.update(financement=mode_fi_row)
        return True
    except Exception as e:
        return e

# ==========================================================================================
@anvil.server.callable           # modif de la réussite du stagiaire au stage, pour permettre la gestion des diplomes, si 
def maj_reussite(stagiaire_row, reussite):               # si réussite = True, son diplome sera envoyé automatiqt en lecture des attestations pdf 
    valid = False
    try:
        stagiaire_row.update(reussite=reussite)
        valid = True
    except Exception as e:
        valid = f"Erreur en écriture de la Réussite au stage {stagiaire_row['stage_txt']} #{stagiaire_row['numero']} pour {stagiaire_row['prenom']} {stagiaire_row['name']}"
    return valid