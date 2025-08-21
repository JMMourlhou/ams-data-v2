import anvil.email
import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

"""
ADD & EFFACEMENT d'1 stagiaire du stage
"""


@anvil.server.callable           # ADD d'un nouveau stagiaire ds le stage
@anvil.tables.in_transaction
def add_stagiaire(stagiaire_row, stage, mode_fi, type_add="", pour_stage=None):   # Stage num pas row
    valid=""
        
    # lecture fichier père stages
    code_stage = app_tables.stages.get(numero=int(stage))
    if not code_stage :
        valid="Stage non trouvé ds fichier stages !"
        return valid
  
    # lecture fichier père user (lecture différente si vient de création 1ere entrée ou bt_modif en recherche)
    if type_add == "":               # 1ere entrée par flash Qr_code: le user est le stagiaire
        user = anvil.users.get_user()
    if type_add == "bt_recherche":   # le stagiaire a été choisit ds recherche (Recherche_stagiaire / RowTemplate1)
        user = app_tables.users.get(email=stagiaire_row['email'])
    if user:
        if user != stagiaire_row :
            valid="Stagiaire non trouvé ds fichier users !"
            return valid
    else:
        valid="User non trouvé ds fichier users !"
        return valid

    # lecture fichier père mode financemnt (si int(stage) != 1003):
    
        
    mode_fin = app_tables.mode_financement.get(code_fi=mode_fi)    
    if not mode_fin :
        valid="Mode de financemnt non trouvé ds fichier param mode financemnt !"
        return valid

    #vérification si user pas déjà inscrit ds fichier stagiaire inscrit, POUR CE STAGE:
    
    test = app_tables.stagiaires_inscrits.search(q.fetch_only("stage_txt"),
                                                 user_email=user,                 # ce user
                                                 stage=code_stage)                # ET pour ce stage
    if len(test)>0:
        valid="Stagiaire déjà inscrit à ce stage !"
        # ******************************************************************* EFFACT code stage ds user avant retour
        user.update(temp = 0)
        return valid 

    """ Ajout des droits QCM pour ce stagiaire """
    if code_stage:
        type_stage = code_stage['code']
        type_stage_row = app_tables.codes_stages.get(code=type_stage['code'])
        if type_stage_row:
            if type_stage_row['droit_qcm'] is not None:
                dico_droits_qcm = type_stage_row['droit_qcm']
            else:
                dico_droits_qcm = {}

    # Si stage 1003, tuteur, je renseigne la colonne 'pour_stage_num'
    if int(stage) == 1003:
        #lecture du stage pour enregistrement de son row
        pour_stage_n = app_tables.stages.get(numero=pour_stage)
    else:  # ce n'est pas un stage tuteur
        pour_stage_n = None
        
    
    new_row=app_tables.stagiaires_inscrits.add_row(
                              stage = code_stage,  
                              user_email = user,
                              name = user['nom'].lower(),    # nom pour permettre le tri sur le nom
                              prenom = user['prenom'].lower(),
                              financement = mode_fin,
                              droits_stagiaire_qcms = dico_droits_qcm,
                              stage_txt = code_stage['code_txt'],
                              numero = code_stage['numero'],
                              enquete_satisf=False,         # le stagiaire ou tuteur n'a pas encore rempli le formulaire de satisfaction
                              enquete_suivi=False,          # le stagiaire ou tuteur n'a pas encore rempli le formulaire de suivi
                              pour_stage_num=pour_stage_n   # voir traitement juste au dessus
                              )
             
    stagiaire_row = app_tables.stagiaires_inscrits.search(stage=new_row['stage'])
    if stagiaire_row:
        # ******************************************************************* EFFACT code stage ds user et INCREMENT du nb de stgiaires ds le stage:
        user.update(temp = 0,
                    role = code_stage['type_stage']  # Le user est du type du stage (ex; F_PSE est de type_stage "F", donc user de type 'F', formateur')
                   )
        
        # INCREMENT nb de stagiaires début stage ds fichier père stage
        try:  # si nb à None il y aurait une erreur
            if code_stage:
                nb = int(code_stage['nb_stagiaires_deb'])+1
                code_stage.update(nb_stagiaires_deb=nb)
                #print("passage ds try ok")
            else:
                valid="erreur: code_stage vide"
        except:        # nb à None,  
            nb=1
            code_stage.update(nb_stagiaires_deb=nb)
            #print("passage ds except ok")
            
        valid=f"Inscription effectuée ! ( 1/{str(nb)} )"
    else:
        valid="Stagiaire non retrouvé dans fichier stagiaires inscrits"

    """  +++++++++++++++++++++++++   Création des pré requis pour ce stagiaire """
    # lecture du fichier stages pour lecture du dictionnaire de ses pré-requis
    if code_stage:
        type_stage = code_stage['code']
        type_stage_row = app_tables.codes_stages.get(code=type_stage['code'])
    if type_stage_row:
        dico_pre_requis = type_stage_row['pre_requis']
        if dico_pre_requis != None:   # il y a des clefs pre-requis
            print("test ok")
            #tri du dictionaire pre requis sur les clefs 
            liste_des_clefs = dico_pre_requis.keys()   #création de la liste des clefs du dictionaires prérequis
            liste_triée_des_clefs = sorted(liste_des_clefs)  # création de la liste triée des clefs du dictionaires prérequis
            dico_pre_requis_trié = {}
            for key in liste_triée_des_clefs:
                 dico_pre_requis_trié[key] = dico_pre_requis[key]
            
            for clef,value in dico_pre_requis_trié.items():
                #print("clef: ",clef)
                pr_row = app_tables.pre_requis.get(code_pre_requis=clef)
                new_row_pr = app_tables.pre_requis_stagiaire.add_row(
                              stage_num = code_stage,  
                              stagiaire_email = user,
                              item_requis = pr_row,
                              check=False,
                              code_txt = code_stage['code_txt'],
                              numero = code_stage['numero'],
                              requis_txt = pr_row['requis'],
                              nom = user['nom'],
                              prenom = user['prenom']
                )    
    return valid

# =========================================================================================================================================
@anvil.server.callable           #AJOUT d'un pré_requis pour un stagiaire d'un stage 
@anvil.tables.in_transaction
def add_1_pre_requis(stage_row, user, pr_row):
    valid = False
    #lecture du stagiaire
    try:  # user est le row_user (qd je modifie les pr par type de stage)
        user_row = app_tables.users.get(q.fetch_only("nom","prenom"),
                                    email=user)
        valid=True
    except: # user est le mail du stgiaire (qd je modifie 1 pr d'1 stgiaire, provenance Pre_R_pour_1_stagiaire )
        user_row = app_tables.users.get(q.fetch_only("nom","prenom"),
                                    email=user["email"])
        valid=True
    
    app_tables.pre_requis_stagiaire.add_row(
                                            stage_num = stage_row,  
                                            stagiaire_email = user_row,
                                            item_requis = pr_row,
                                            check=False,
                                            code_txt = stage_row['code_txt'],
                                            numero = stage_row['numero'],
                                            requis_txt = pr_row['requis'],
                                            nom = user_row['nom'],
                                            prenom = user_row['prenom']
                                             )    
    return valid

# =========================================================================================================================================
@anvil.server.callable           #DEL d'1 stagiaire du stage
@anvil.tables.in_transaction
def del_stagiaire(stagiaire_row, stage_num):     # stagiaire_row = table users row      stage_numero = table stagiaire inscrit, colonne numero (int)
    valid=""
    # DECREMENTATION nb de stagiaires ds ce stage
    # lecture fichier père stages
    stage_r = app_tables.stages.get(numero=stage_num)
    if not stage_r :
        valid="Stage non trouvé ds table stages !"
        return valid
    else:
        nb = int(stage_r['nb_stagiaires_deb'])-1
        stage_r.update(nb_stagiaires_deb=nb)

    #effacement des pré-requis du stagiaire
    #lecture des rows à effacer ds pre requis
    liste_pr = app_tables.pre_requis_stagiaire.search(stagiaire_email = stagiaire_row,
                                                      stage_num = stage_r
                                                  )
    if len(liste_pr) > 0:
        for pr in liste_pr:
            pr.delete()

    # Lecture table stagiaires inscrits à ce stage pour effacement du stagiaire
    row = app_tables.stagiaires_inscrits.get(user_email=stagiaire_row,       # ce user
                                            numero=stage_num)            # ET pour ce stage
    if not row :
        valid="Stagiaire à enlever du stage non trouvé ds table stagiaires inscrits !"
        return valid
    
    # Del of stagiaire in the stage
    row.delete()
    valid="Stagiaire retiré de ce stage !"
   
    return valid

# =========================================================================================================================================
@anvil.server.callable           #Réinitilisation Saisie du formulaire de satisfaction d'1 stagiaire du stage
def init_formulaire_satis_stagiaire(stagiaire_row, bool):
    valid=False
    if not stagiaire_row :
        return valid
    
    # modif du row stagiaire_inscrit
    stagiaire_row.update(enquete_satisf = bool)
    
    # SI BOOL False, recherche et effacement du formulaire de satisf en table Stage_suivi si existant
    if bool is False: # si l'utilisateur a modifié l'indicateur du formulaire de satisf à False, et a confrmé annuler le formulaire pour permettre une ressaisie d'un autre formulaire
        stage_satis_row = app_tables.stage_satisf.get(stage_row= stagiaire_row['stage'],
                                        user_email=stagiaire_row['user_email'])
        if stage_satis_row is not None: # si le formulaire existe, on l'efface
            # Effacement du row du formulaire table Stage_suivi
            stage_satis_row.delete()
        valid=True  
        
    return valid

    
#Réinitilisation check box d'indicateur de saisie du formulaire de suivi d'1 stagiaire du stage, appelé par Stage_visu_modif / S.RowTemplate4
# =========================================================================================================================================
@anvil.server.callable           
def init_formulaire_suivi_stagiaire(stagiaire_row, modif, effacement=False):  #stagiaire_inscrit row
    valid=False
    if not stagiaire_row :
        return valid
        
    # modif du row stagiaire_inscrit
    try:
        stagiaire_row.update(enquete_suivi = modif)
        valid = True
    except:
        valid= False
        return valid
        
    # SI effacement True, recherche et effacement du formulaire de suivi en table Stage_suivi si existant
    if effacement is True: # si l'utilisateur a modifié l'indicateur du formulaire de suivi à False, et a confrmé annuler le formulaire pour permettre une ressaisie d'un autre formulaire
        stage_suivi_row = app_tables.stage_suivi.get(stage_row= stagiaire_row['stage'],
                                        user_email=stagiaire_row['user_email']['email'])
        if stage_suivi_row is not None: # si le formulaire existe, on l'efface
            # Effacement du row du formulaire table Stage_suivi
            try:
                stage_suivi_row.delete()
                valid=True
            except:
                valid = False
    
    return valid