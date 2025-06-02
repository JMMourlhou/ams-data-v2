from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import *  #pour les alertes


# =========================================================================
# appelé par form Formulaire_par_type_stage
@anvil.server.callable           #modif du dico pré_requis pour un type de stage ds table 'codes stages'
def modif_dico_formulaire_codes_stages(stage_row, formulaire_dico, type_formulaire):
    valid=""
    if not stage_row :
        valid=False
    else:
        print("stage_row: ", stage_row['code'])
        print("type_formulaire: ", type_formulaire)
        print("dico: ", formulaire_dico)
        if type_formulaire == "SAT_F":
            stage_row.update(satisf_q_ferm_template=formulaire_dico)
            valid=True
        if type_formulaire == "SAT_O":
            stage_row.update(satisf_q_ouv_template=formulaire_dico)
            valid=True
        if type_formulaire == "SUI_F":
            stage_row.update(suivi_stage_q_ferm_template=formulaire_dico)
            valid=True
        if type_formulaire == "SUI_O":
            stage_row.update(suivi_stage_q_ouv_template=formulaire_dico)
            valid=True
        if type_formulaire == "COM_F":
            stage_row.update(com_ferm=formulaire_dico)
            valid=True
        if type_formulaire == "COM_O":
            stage_row.update(com_ouv=formulaire_dico)
            valid=True
    return valid


# ==========================================================================================
#Création d'un nouveau code
@anvil.server.callable 
def add_text_formulaire(code, text, obligation):
    new_row=app_tables.texte_formulaires.add_row(
                              code=code,
                              text=text,
                              obligation=obligation
                             )
                 
    row = app_tables.texte_formulaires.search(code=new_row['code'])
    if len(row)>0:
        valid=True
    else:
        valid=False
    return valid

# ==========================================================================================
@anvil.server.callable           #Del d'un code texte
def del_text_formulaire(code_row):
    valid = False
    code_row.delete()
    valid = True
    
    return valid

# ==========================================================================================
@anvil.server.callable           #modif d'un lieu et adresse 
def modif_text_formulaire(code_row, code, text, obligation):
    valid = False
    code_row.update(
                    code=code,
                    text=text,
                    obligation=obligation
                    )
    valid = True
    return valid

   
# maj  enquete_suivi=False, de table stagiaire inscrit, stage concerné, stagiaire concerné
# appelé par Formulaire_suivi / F.RowTemplate2
# ==========================================================================================
@anvil.server.callable           #modif d'un lieu et adresse 
def del_formulaire_suivi(code_row):
    valid = False
    
    # remise  enquete_suivi=False, table stagiaire inscrit, stage concerné, stagiaire concerné
    # pour qu'il puisse ré effectuer le formulaire de suivi:
    # lecture du row user
    row_user = app_tables.users.get(email=code_row['user_email'])
    # lecture du row table stagiaire inscrit
    row_stagiaire_inscrit = app_tables.stagiaires_inscrits.get(stage=code_row['stage_row'],
                                            user_email=row_user)
    row_stagiaire_inscrit.update(enquete_suivi=False)

    # Effacement du row du formulaire table Stage_suivi
    code_row.delete()

    valid = True
    return valid

# maj  enquete_suivi=False, de table stagiaire inscrit, stage concerné, stagiaire concerné
# appelé par Formulaire_suivi / F.RowTemplate2
# ==========================================================================================
@anvil.server.callable           
def del_formulaire_satisf(code_row):
    valid = False
    
    # remise  enquete_suivi=False, table stagiaire inscrit, stage concerné, stagiaire concerné
    # pour qu'il puisse ré effectuer le formulaire de suivi:
    # lecture du row user
    row_user = app_tables.users.get(email=code_row['user_email']['email'])
    # lecture du row table stagiaire inscrit
    row_stagiaire_inscrit = app_tables.stagiaires_inscrits.get(stage=code_row['stage_row'],
                                            user_email=row_user)

    row_stagiaire_inscrit.update(enquete_satisf=False)

    # Effacement du row du formulaire table Stage_suivi
    code_row.delete()

    valid = True
    return valid