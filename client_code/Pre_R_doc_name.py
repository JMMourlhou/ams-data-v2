import anvil.server
import anvil.tables as tables

# DETERMINATION DU NOM DU DOC REQUIS, utilisé par plusieurs modules
def doc_name_creation(row_stage_num, row_item_requis, row_user):
    len_name = len(row_user['nom'])           # premiers caractères du Nom  ???
    name = row_user['nom'][0:len_name]        # pour l'instant tous les caractères du Nom    
    name = name.replace(" ","-")              # !!! si espaces ds nom 
    prenom = row_user['prenom'][0:1]          # 1 caract prénom
    
    # Acquisition du num de stage
    stg = str(row_stage_num['numero'])     # Num de stage

    # Acquisition de l'item requis
    item = row_item_requis['code_pre_requis']
    
    file_name= stg + "_"+ item +"_"+ name.capitalize() + "-"+ prenom.capitalize()    # l'extension sera ajoutée ds les autres modules

    return file_name    # file name sans l'extension
