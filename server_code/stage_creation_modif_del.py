import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import *  #pour les alertes

# ------------------------------------------------------------------------------------------- MAJ Table type de stages   (Form Stage_MAJ_Table)
#Création d'un nouveau type de stage
@anvil.server.callable 
def add_type_stage( code,     # row codes_stage concernée
                    intitule,
                    type_stage):
    
    new_row=app_tables.codes_stages.add_row(
                                                code=code,     # row codes_stage concernée
                                                intitulé=intitule,
                                                type_stage=type_stage,
                                                dico_menu={},     # initialisation des dicos
                                                pre_requis={},
                                                droit_qcm={},
                                                satisf_q_ferm_template={},
                                                satisf_q_ouv_template={},
                                                suivi_stage_q_ferm_template={},
                                                suivi_stage_q_ouv_template={},
                                                com_ferm={},
                                                com_ouv={}
                                                    )
    row = app_tables.codes_stages.search(code=new_row['code'])
    if len(row)>0:
        valid=True
    else:
        valid=False
    return valid

# ==========================================================================================
@anvil.server.callable           #modif d'un type de stage 
def modif_type_stage(row_code,    # row type de stage
                    code,
                    intitule,
                    type_stage,
                    old_intitul):     # permet de rechercher ce vieux code ds la table stagiaires_inscrits
    
    valid_1=False
    row_code.update(
                    code=code,     # row codes_stage concernée
                    intitulé=intitule,
                    type_stage=type_stage
                    )
    valid_1=True
    
    # modif des droits aux qcm pour les stagiaires impliqués
    valid_2=False
    list=app_tables.stages.search(q.fetch_only("code", "code_txt","type_stage"),
                                    code=row_code)
    nb = len(list)
    if nb > 0:
        for stage in list:
            stage.update(
                code=row_code,   # code_stage row
                code_txt=code,
                type_stage=type_stage
                )
            # recherche des stagiaiares de ce stage
            list1=app_tables.stagiaires_inscrits.search(q.fetch_only("stage_txt"),
                                                stage=stage)                     # recherche dans table à partir du old intitul
            nb1 = len(list1)
            print(f"nb stagiaires du stage {stage['numero']}; {nb1}")
            if nb1 > 0:
                for stagiaire in list1:
                    stagiaire.update(
                        stage_txt=code,       # modif avec l'intitul nouveau
                        )
    valid_2=True
    
    if valid_1 is True and valid_2 is True:
        return True
    else:
        return False
    
                
# ==========================================================================================
#Effact d'un type de stage existant (si pas de stages), le test a été effectué en client side
@anvil.server.callable 
def del_type_stage(type_stage_row):   # stage_num: num de stage en txt
    result = False
    if type_stage_row:
        type_stage_row.delete()
        result = True
    return result

#=====================================================================================================================================================

#Création d'un nouveau stage
@anvil.server.callable 
def add_stage(code_stage,     # row codes_stage concernée
              code_txt,
              numero,         # numéro de stage en clair: txt
              lieu_stage,     # row lieux concerné
              date_debut,
              nb_stagiaires_deb,
              date_fin,
              nb_stagiaires_fin,
              nb_stagiaires_diplomes,
              commentaires,
              pv
             ):
    #print("lieu: ",lieu)         
    numero=int(numero)   
    try:
        new_row=app_tables.stages.add_row(
                                type_stage = code_stage['type_stage'],   # copie du type de stage, S,F,V,T
                                code = code_stage,
                                code_txt = code_stage['code'],
                                numero = numero,
                                lieu = lieu_stage,
                                date_debut = date_debut,
                                nb_stagiaires_deb = 0,
                                date_fin = date_fin,
                                nb_stagiaires_fin = None,
                                nb_stagiaires_diplomes = None,
                                commentaires = commentaires,
                                allow_bgt_generation = False,
                                saisie_satisf_ok = False,     # Ne pas saisir le form de stisfaction
                                num_pv = pv,                  # Num de pv 
                                satis_dico1_q_ferm=code_stage["satisf_q_ferm_template"],  # copie du template satisf de la table "code_stages", questions fermées
                                satis_dico2_q_ouv=code_stage["satisf_q_ouv_template"],     # copie du template satisf de la table "code_stages", questions ouvertes
                                suivi_dico1_q_ferm=code_stage["suivi_stage_q_ferm_template"],  # copie du template suivi de la table "code_stages", questions fermées
                                suivi_dico2_q_ouv=code_stage["suivi_stage_q_ouv_template"],    # copie du template suivi de la table "code_stages", questions ouvertes
                                com_ouv=code_stage["com_ouv"],                              # copie du template com de la table "code_stages", questions ouvertes
                                com_ferm=code_stage["com_ferm"]                             # copie  du template com de la table "code_stages", questions fermées
                                )
    except Exception as e:
        valid=False
        return e
                 
    stage = app_tables.stages.search(numero=new_row['numero'])
    if len(stage)>0:
        
        #incrément du compteur de stages
        num = app_tables.cpt_stages.search()[0]
        cpt=int(num['compteur'])+1 
        try:
            num.update(compteur=cpt)
            valid=True
        except Exception as e:
            valid=False
            return e
    else:
        valid=False
    return valid


# ==========================================================================================
@anvil.server.callable           #modif d'un stage
@anvil.tables.in_transaction
def modif_stage(row_stage,    # row table stages
              row_type,     # row type de stage PSC, PSE1 ...  
              numero,   # attention numero est txt
              lieu,
              date_debut,
              nb_stagiaires_deb,
              date_fin,
              nb_stagiaires_fin,
              nb_stagiaires_diplomes,
              commentaires,
              allow_bgt_generation,  # True/False
              allow_form_satisf,     # True/False 
              allow_form_suivi,       # True/False 
              allow_form_com,
              pv  
             ):
    numero=int(numero)
    #print(f" +++++++++++++++++++++ check_box_allow_com (en début de serveur): {allow_form_com}")
    # lecture fichier père code stages
    code_stage = app_tables.codes_stages.get(code=row_stage['code']['code'])
    if not code_stage:   
        alert("Code stage non trouvé ds fichier param Code_stages")
        valid=False
        return valid             
    # lecture fichier père lieux
    lieu_stage = app_tables.lieux.get(lieu=lieu)    
    if not lieu_stage :
        alert("Lieu stage non trouvé ds fichier param lieux")
        valid=False
        return valid    

    # lecture du stage à modifier par son numéro             
    stage = app_tables.stages.get(numero=numero) 
    if not stage:
        print(f"Changement de numéro de stage: {numero}")
    try:   
        row_stage.update(code = row_type,                      # type de stage modifiable pour faciliter les chgt eventuels de type de stage
                    numero = int(numero),                      # numero du stage modifiable en cas d'erreur
                    lieu = lieu_stage,
                    date_debut = date_debut,
                    nb_stagiaires_deb = nb_stagiaires_deb,
                    date_fin = date_fin,
                    nb_stagiaires_fin = nb_stagiaires_fin,
                    nb_stagiaires_diplomes = nb_stagiaires_diplomes,
                    commentaires = commentaires,
                    allow_bgt_generation = allow_bgt_generation,
                    saisie_satisf_ok =allow_form_satisf,         # formulaire de satisf autorisé ? T/F
                    saisie_suivi_ok = allow_form_suivi,          # formulaire de suivi autorisé ? T/F
                    display_com = allow_form_com,                # formulaire de communication autorisé ? T/F
                    num_pv=pv     
                    )
        valid=True
    except Exception as e:
        valid=e
    return valid

# Appelé par Stage_visu_modif, click sur self.check_box_allow_satisf.checked = TRUE
# Inclure pour tous les stagiaires du stage_num les formulaires de satisfaction de la table code_stages
@anvil.server.callable
def update_satisf_pour_un_stage(stage_row, satis_dico2_q_ouv, satis_dico1_q_ferm):   # stage_row : 1 row table 'stages' 
    print(f"dico ouvert en serveur: {satis_dico2_q_ouv}")
    stage_row.update( satis_dico1_q_ferm = satis_dico1_q_ferm,
                      satis_dico2_q_ouv = satis_dico2_q_ouv,
                      saisie_satisf_ok = True
                        )
    return

# Appelé par Stage_visu_modif   
# Inclure pour tous les stagiaires du stage_num les formulaires de suivi de la table code_stages
@anvil.server.callable
def update_suivi_pour_un_stage(stage_row, suivi_dico2_q_ouv, suivi_dico1_q_ferm):   # stage_row : 1 row table 'stages' 
    stage_row.update( suivi_dico1_q_ferm = suivi_dico1_q_ferm,
                      suivi_dico2_q_ouv = suivi_dico2_q_ouv,
                      saisie_suivi_ok = True
                        )
    return


# Appelé par Stage_visu_modif   click sur self.check_box_allow_com.checked = TRUE
# Inclure pour tous les stagiaires du stage_num les formulaires de com de la table code_stages
@anvil.server.callable
def update_com_pour_un_stage(stage_row, com_ouv, com_ferm):   # stage_row : 1 row table 'stages' 
    stage_row.update( com_ferm = com_ferm,
                      com_ouv = com_ouv,
                      display_com = True
                        )
    return



    
# ==========================================================================================
#Effact d'un stage existant (si pas de stagiaires), le test a été effectué en client side
@anvil.server.callable 
def del_stage(row_id, stage_num):   # row id du stage à annuler, numéro du stage
    result = False
    #lecture du row du stage:
    stage_row = app_tables.stages.get_by_id(row_id)
    if stage_row:
        try:
            stage_row.delete()
            result = True
        except Exception as e:
            return e
            
        #décrément du compteur de stages si c'est le dernier stage créé
        cpt_num_stage_row = app_tables.cpt_stages.search()[0]
        if stage_num ==  cpt_num_stage_row['compteur']:
            cpt=int(cpt_num_stage_row['compteur'])-1 
            try:
                cpt_num_stage_row.update(compteur=cpt)
                result = True
                
            except Exception as e:
                return e   
        return result

# Appelé par Stage_visu_modif   
# Sauve le fichier pdf des diplomes
@anvil.server.callable
def sov_diplomes(stage_row, file):   # stage_row : 1 row table 'stages' 
    try:
        stage_row.update( diplomes = file )
        return True, ""
    except Exception as e:
        return False, e

# Appelé par Stage_visu_modif   
# En cas de maj manuelle du check box diplomes sent 
@anvil.server.callable
def attestions_sent(stage_row, sent_checked):   # stage_row : 1 row table 'stages' 
    try:
        stage_row.update( diplom_sent = sent_checked )
        return True, ""
    except Exception as e:
        return False, e