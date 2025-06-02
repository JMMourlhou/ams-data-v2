import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# =========================================================================
@anvil.server.callable           #modif du dico pré_requis pour un type de stage ds table 'codes stages'
def modif_pre_requis_codes_stages(code_stage, pr_requis_dico):
    valid=""
    # lecture fichier père stages
    stage_r = app_tables.codes_stages.get(code=code_stage)
    if not stage_r :
        valid=False
    else:
        stage_r.update(pre_requis=pr_requis_dico)
        valid=True
    return valid

# =========================================================================
@anvil.server.callable           #del du pré_requis (pour un type de stage) ds tous les stages impliqués
def del_1pr(clef_a_annuler,code_stage,efface=False):  # efface est TRUE si on efface quand même un doc existant pour le PR à effacer 
    result = False
    # lecture row du item_requis à annuler
    row = app_tables.pre_requis.get(q.fetch_only(),
                                    code_pre_requis=clef_a_annuler)
    # lecture du fichier père type de stage
    type_stage = app_tables.codes_stages.get(q.fetch_only(),
                                            code=code_stage)
    #lecture des stages impliqués, ceux qui sont des stages du type de stage sélectionné
    liste_stages = app_tables.stages.search(code=type_stage)
    # lecture des stagiaires inscrits à ces stages
    for stage in liste_stages:
        liste_stagiaires = app_tables.pre_requis_stagiaire.search(stage_num = stage,
                                                                item_requis = row
                                                                )
        for stagiaire in liste_stagiaires:
            # Pour chq stagiaire, effact du pré_requis SI VIDE                    
            if stagiaire['doc1'] is None or efface is True:
                stagiaire.delete()
            result = True
    return result
