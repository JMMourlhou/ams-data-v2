import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil.pdf import PDFRenderer

# Création d'un QCM
@anvil.server.callable
def qcm_création(qcm_nb, destination, qcm_owner, visible, examen):                # qcm_owner: user row     qcm_nb text
    new_row=app_tables.qcm_description.add_row(
                                                qcm_nb=int(qcm_nb),
                                                destination=destination,
                                                qcm_owner=qcm_owner,   # user row
                                                visible=visible,
                                                exam=examen
                                                    )
    qcm_row = app_tables.qcm_description.search(qcm_nb = new_row["qcm_nb"])
    if qcm_row:
        valid=True
    else:
        valid=False
    return valid

# modif description d'un QCM
@anvil.server.callable
def qcm_modif(qcm_row, qcm_nb, destination, qcm_owner, visible, examen):                # qcm_owner: user row     qcm_nb text
    qcm_row.update(
                    qcm_nb=int(qcm_nb),
                    destination=destination,
                    qcm_owner=qcm_owner,   # user row
                    visible=visible,
                    exam=examen
                        )
    qcm_row = app_tables.qcm_description.search(qcm_nb = int(qcm_nb))
    if qcm_row:
        valid=True
    else:
        valid=False
    return valid

# del d'un QCM
@anvil.server.callable
def qcm_del(qcm_row):                # qcm_owner: user row     qcm_nb text
    id = qcm_row.get_id()
    qcm_row.delete()
    
    test=app_tables.qcm_description.get_by_id(id)
    if not test:
        valid=True
    else:
        valid=False
    return valid

# modif dictionaire source d'un qcm exam, appelé par Qcm_visu_modif_main, template 27
@anvil.server.callable
def qcm_enfant_add(qcm_parent_row, qcm_enfant_nb, nb_questions):                # ajout ds dico colonne qcm_source de la table QCM_description
    # lecture du qcm à partir de son numero
    result = False
    dico=qcm_parent_row['qcm_source']
    # éviter l'erreur si pas de dico source
    if dico is None or dico == {}:
        dico ={}
    # On efface l'ancienne clé si elle existe (quand on modifie le nb de questions)
    try:
        del dico[str(qcm_enfant_nb)]
    except:
        print("Nouvelle clé")
    # ajout au dico source
    key = str(qcm_enfant_nb)
    value = str(nb_questions)
    dico[key]=value
    # modif en table qcm_description, colonne qcm_source
    qcm_parent_row.update(qcm_source=dico)
    result = True
    return result

# ellever un qcm du dictionaire source d'un qcm exam, appelé par Qcm_visu_modif_main, template 29
@anvil.server.callable
def qcm_enfant_del(qcm_parent_row, qcm_enfant_nb):  
    result = False
    dico=qcm_parent_row['qcm_source']
    # on enleve la clé du qcm enfant du dico source
    del dico[str(qcm_enfant_nb)]
    # modif en table qcm_description, colonne qcm_source
    qcm_parent_row.update(qcm_source=dico)
    result = True
    return result

@anvil.server.callable
def add_ligne_qcm(num_question, question, correction, rep, bareme, image, qcm_nb, type, param):
    # qcm_nb est la row venant du dropdown choix du qcm
    new_row=app_tables.qcm.add_row(num= int(num_question),
                                   question = question,
                                   correction = correction,
                                   rep_multi = rep,
                                   bareme = str(bareme),
                                   photo = image,
                                   qcm_nb = qcm_nb,
                                   type = type,
                                   param = param)
            
    qcm_row = app_tables.qcm.search(qcm_nb = qcm_nb,
                                    num=num_question
                                    )
    if qcm_row:
        valid=True
    else:
        valid=False
    return valid

# =================================================================================================================
# MODIF du QCM (en maj d'un qcm)
@anvil.server.callable           #modif d'une ligne de Qcm
def modif_qcm(qcm_descro_row, num_question, question, rep, bareme, photo, correction):

    # lecture de la ligne à modifier par son numéro             
    qcm_row = app_tables.qcm.get(num=num_question,
                                qcm_nb=qcm_descro_row)
    if not qcm_row:
        print("Ligne qcm non trouvée ds fichier qcm")
        return False
    else:   
        rep_multi = rep
        qcm_row.update(question = question,
                     rep_multi = rep,
                     bareme = str(bareme),
                     photo = photo,
                     correction= correction
                    )
        return True

# =================================================================================================================
# Delete d'1 ligne du QCM (en mode maj d'un qcm)
@anvil.server.callable           #modif d'une ligne de Qcm
def delete_qcm(qcm_descro_row, num_question):
    # lecture de la ligne à enlever par son numéro             
    quest_qcm = app_tables.qcm.get(num=num_question,
                                   qcm_nb=qcm_descro_row)
    if not quest_qcm:
        print("Ligne qcm non trouvée ds fichier qcm")
        return False
    else:   
        #------------------------------------------------------------- tranfert/ ds le qcm 16 de la question annulée
        """
        w_sur_qcm_nb = 16
        r = app_tables.qcm_description.get(qcm_nb=w_sur_qcm_nb)   # acquisition du row du qcm
        liste_qcm_cible = app_tables.qcm.search(qcm_nb=r)
        if liste_qcm_cible: 
            nb_lignes_qcm_cible = len(liste_qcm_cible)
        else:
            nb_lignes_qcm_cible = 0

        num_question = nb_lignes_qcm_cible + 1
        question = quest_qcm['question']  
        correction = quest_qcm['correction']
        rep = quest_qcm['rep_multi']
        bareme = quest_qcm['bareme']
        image = quest_qcm['photo']
        qcm_nb = r
        type = quest_qcm['type']
        param = quest_qcm['param']
        
        result = add_ligne_qcm(num_question, question, correction, rep, bareme, image, qcm_nb, type, param)
        if not result:
            print("Erreur en copy/delete de ligne")
            return
        """
        #-------------------------------------------------------------
        quest_qcm.delete()        
        return True

# ==================================================================================================
# modify the question number of the qcm questions after a deletion of a question
# ==================================================================================================
@anvil.server.callable
def renumber_qcm(qcm_descro_row):
#lecture fichier père qcm descro
        table = app_tables.qcm.search(qcm_nb=qcm_descro_row)
        result=False
        cpt = 0
        if table:
            for row in table:
                cpt += 1
                row.update(num = cpt
                          )
            result=True
        param_table_qcm = qcm_descro_row["destination"]
        print(f"loop Re-numération après delete ds table {param_table_qcm}: {result}")
        return result    

# =====================================================================================================================
#                 UTILISATION DU QCM PAR UN STAGIAIRE, SAUVEGARDE DES RESULTATS DS table.qcm_result
# =====================================================================================================================
# ENREGITREMENT, en fin de questions du QCM pour un stagiaire
@anvil.server.callable 
def qcm_result(user, qcm_numero, nb_bonnes_rep, max_points, points, reponses):      # debut: debut de qcm, enregt du num et user
    import French_zone_server_side
    nb_questions = len(reponses)
    if nb_questions == 0:
        valid = False
        return
    p100_sur_nb_rep = int(nb_bonnes_rep / nb_questions * 100)    # Ce résultat permet de débloquer le prochain QCM si il y en a un 
    p100_sur_points = int(points / max_points * 100)

    # lecture fichier qcm_decription
    qcm_row=app_tables.qcm_description.get(qcm_nb=qcm_numero)

    # si résultat en % >= résultats requis pour réussite ds qcm_descro : je valide le prochain qcm (si colonne next_qcm non vide): je change le dict ds stagiaire_inscrit
    success = False                            # initialisation du success à False
    if qcm_row:
        seuil = qcm_row['taux_success']
        #print("seuil :", seuil)
        if p100_sur_nb_rep >= seuil:
            success = True                     # success TRUE
            #recherche du qcm suivant éventuel
            if qcm_row['next_qcm'] != None:
                next_qcm = str(qcm_row['next_qcm'])   
                #print("next qcm: ", next_qcm)
                
                # je recherche les stages du user à partir de son mail
                liste_stages_stagiaire = app_tables.stagiaires_inscrits.search(user_email=user)
                if liste_stages_stagiaire:
                    for st in liste_stages_stagiaire:
                        print(f"Stagiaire inscrit à: {st['stage']['code']['code']}")
                        dict = st['droits_stagiaire_qcms']
                        print(f"Ce stagiaire a droit aux QCM suivants: {dict}")
                        try:
                            valeur = dict.get(next_qcm)
                            #print(" ----  next qcm: ", next_qcm)
                            #print(" ----  valeur: ", valeur)
                            
                            new_valeur = [valeur[0],"True"]
                            dict[next_qcm] = new_valeur   #réaffectation de cette clé
                            st.update(droits_stagiaire_qcms = dict)
                        except:
                            pass
    print(f"Time fin du QCM: {French_zone_server_side.time_french_zone()}")
    app_tables.qcm_result.add_row(
                                    user_qcm= user,
                                    name = user['nom'],
                                    prenom = user['prenom'],
                                    qcm_number=qcm_row,
                                    intitule=qcm_row['destination'],
                                    time= French_zone_server_side.time_french_zone(),
                                    liste_rep = reponses,
                                    nb_rep_ok = nb_bonnes_rep,
                                    p100_sur_nb_rep = p100_sur_nb_rep,
                                    p100_sur_points = p100_sur_points,
                                    success = success
                            )

    qcm_result_row = app_tables.qcm_result.search(qcm_number = qcm_row,
                                                  user_qcm= user,
                                            )
    if qcm_result_row:
        valid=True
    else:
        valid=False
    return valid


# ==================================================================================================
# modify the column temp of table user during qcm (nb of questions)
# ==================================================================================================
@anvil.server.callable
def temp_user_qcm(user, nb_questions_in_qcm, numero_qcm):
    #user.update(temp = int(nb_questions_in_qcm))
    result = False
    if user:
        try:
            user.update(temp = int(nb_questions_in_qcm),        # temp2 contient 'test' si le concepteur a testé son qcm     
                        temp3 = str(numero_qcm)                 # temp3 contient num du qcm réel
                       )                                        # temp contient le nb de questions
            result = True
        except:
            result = False
    return result

# Génération du pdf des résultats du QCM
@anvil.server.callable
def create_qcm_plot_pdf(user, nb, visu_next_qcm = False, visu_legend=False):     # nb : num du qcm
    #from anvil.pdf import PDFRenderer
    """
    quality :
    "original": All images will be embedded at original resolution. Output file can be very large.
    "screen": Low-resolution output similar to the Acrobat Distiller “Screen Optimized” setting.
    "printer": Output similar to the Acrobat Distiller “Print Optimized” setting.
    "prepress": Output similar to Acrobat Distiller “Prepress Optimized” setting.
    "default": Output intended to be useful across a wide variety of uses, possibly at the expense of a larger output file.
    """

    media_object = PDFRenderer(page_size ='A4',
                               filename = "resultat_qcm.pdf",
                               landscape = False,
                               margins = {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0},  # en cm
                               scale = 1,
                               quality =  "default"
                              ).render_form('Plot',user, nb, visu_next_qcm, visu_legend)
    return media_object

# ------------------------------------------------------------------------------------------------------------------
# ajout d'un droit au qcm pour un stage, table codes_stages, appelé en paramètres par QCM_par_stage / template 18
@anvil.server.callable
def modif_qcm_stage(nb, qcm_descro, stage, visible): # nb: int, num du qcm    stage: stage row ds table  codes_stages    visible: Qcm visible ? True / False

    valid_1=False
    # préparation de l'option visible ou pas ds la valeur de la clé
    if visible is True:  # la valeur est "True", le qcm est visible dès l'accès du stgiaire au menu QCM
        visu = "True"
    else:
        visu = "False"
        
    # création de la clé / valeur
    cle = str(nb) # clé du QCM doit être str
    valeur = [qcm_descro, visu]   # intiltulé du QCM

    # lecture dictionnaire des qcm ds la table 
    dict={}  
    dict = stage["droit_qcm"]
    if dict is None or dict == {}:
        dict={}    
    print(f"dico: {str(dict)}")
     # ajout du qcm ds le dictionaire
    dict[cle]=valeur
    
    # sauvegarde du dict des droits aux qcm ds table 'codes_stages' dans la ligne de ce stage 
    stage.update(droit_qcm=dict)
    valid_1=True
    
    # répercution sur les stagiaires de ce type de stage
    valid_2=False
      # recherche des stagiaiares de ce type de stage
    list1=app_tables.stagiaires_inscrits.search(q.fetch_only("stage_txt","droits_stagiaire_qcms"),
                                                stage_txt=stage["code"])                     # recherche dans table à partir du code du stage en table codes_stages
    nb1 = len(list1)
    print(f"nb stagiaires impliqués pour ce type de stage {stage['code']}; {nb1}")
    if nb1 > 0:
        for stagiaire in list1:
            stagiaire.update(
                droits_stagiaire_qcms=dict,       # écriture du nouveau dictionaire des qcm pour ce stage
                )
            
    valid_2=True

    if valid_1 is True and valid_2 is True:
        return True
    else:
        return False
        
    

# ------------------------------------------------------------------------------------------------------------------
# effact d'un droit au qcm pour un stage, table codes_stages, appelé en paramètres par QCM_par_stage / template 19
@anvil.server.callable
def del_qcm_stage(nb, stage): # nb: int, num du qcm    stage: stage row ds table  codes_stages   
    valid_1=False
    # création de la clé 
    cle = str(nb) # clé du QCM doit être str

    # lecture dictionnaire des qcm ds la table 
    dict={}  
    dict = stage["droit_qcm"]
    
     # del du qcm ds le dictionnaire
    del dict[cle]
    
    # sauvegarde du dict des droits aux QCM en table codes_stage
    stage.update(droit_qcm=dict)
    valid_1=True
    
    # répercution sur les stagiaires de ce type de stage
    valid_2=False
      # recherche des stagiaires de ce type de stage
    list1=app_tables.stagiaires_inscrits.search(q.fetch_only("stage_txt","droits_stagiaire_qcms"),
                                        stage_txt=stage["code"])                     # recherche dans table à partir du code du stage en table codes_stages
    nb1 = len(list1)
    print(f"nb stagiaires impliqués pour ce type de stage {stage['code']}; {nb1}")
    if nb1 > 0:
        for stagiaire in list1:
            stagiaire.update(
                droits_stagiaire_qcms=dict,       # écriture du nouveau dictionaire des qcm pour ce stage
                )
    valid_2=True

    if valid_1 is True and valid_2 is True:
        return True
    else:
        return False

        
# ------------------------------------------------------------------------------------------------------------------
# modif table qcm descro, qcm d'un stage sélectionné, appelé par QCM_par_stage, Template 19, qd on modifie QCM visible, tx de réussite, next QCM, ...
@anvil.server.callable
def modif_qcm_descro_pour_un_stage(nb, visible, taux_success, next_qcm, visu_start, row_type_stage): # nb: int, num du qcm    row_type_stage: stage row ds table  codes_stages   
    print("------------------------------------------------- visible=", visible)
    valid_1 = False
    valid_2 = False
    # lecture du qcm row, table qcm description
    qcm_row = app_tables.qcm_description.get(qcm_nb=nb)
    if len(str(qcm_row))>0:
        # test si next_qcm est vide
        if next_qcm == "":
            next_qcm = None
        else:
            next_qcm = int(next_qcm)
        
        # test si taux succès est vide  
        if  len(str(taux_success))==0:
            taux_success = None
        else:
            taux_success = int(taux_success)
            
        # sauvegarde du qcm description
        qcm_row.update(
                        visible=visible,
                        taux_success = taux_success,
                        next_qcm = next_qcm,
                        visu_qcm_par_stage = visu_start
                        )

        # quand visible est checked: Répercution sur : 1) table codes_stages, visible T/F    2) tous les stagiaires de ce type de stage

        # 1) Répercution sur table codes_stages, visible T/F
        # row_type_stage doit être modifiée
        dico_droits_qcm = row_type_stage['droit_qcm']
        # recherche de la clé du stage
        valeur = dico_droits_qcm.get(str(nb))
        print(f"'modif_qcm_descro_pour_un_stage', valeur du dico pour qcm n°{nb} :{valeur[0]}, {valeur[1]}")
        # Effacement de cette clé
        del dico_droits_qcm[str(nb)]
        # ajout de la valeur pour cette clé
        if visible is True:
            v1="True"
        else:
            v1="False"
        dico_droits_qcm[str(nb)] = [valeur[0],v1]
        # sauvegarde du 'row_type_stage' en table codes_stages 
        row_type_stage.update(droit_qcm=dico_droits_qcm)
        valid_1 = True
        
        # 2) Répercution de ce dico sur tous les stagiaires de ce type de stage
        # recherche des stagiaires de ce type de stage
        list1 = app_tables.stagiaires_inscrits.search(q.fetch_only("stage_txt","droits_stagiaire_qcms"),
                                                                stage_txt=row_type_stage['code'])

        # 2) Répercution de ce dico sur tous les stagiaires de ce type de stage
        nb1 = len(list1)
        print(f"nb stagiaires impliqués pour ce type de stage {row_type_stage['code']}; {nb1}")
        if nb1 > 0:
            for stagiaire in list1:
                stagiaire.update(
                    droits_stagiaire_qcms=dico_droits_qcm      # écriture du nouveau dictionaire des qcm pour ce stage
                    )
        valid_2=True
    
        if valid_1 is True and valid_2 is True:
            return True
        else:
            return False

# ------------------------------------------------------------------------------------------------------------------
# modif table qcm descro, colonne source, appelé par QCM_visu_modif_Main, verif effectuée 1) si la col source est None et 2)si nb de questions à afficher pour le qcm est correct 
@anvil.server.callable
def change_source_qcm(qcm_descro_row, nb_questions_real):
    valid = False
    dico = {}
    cle = str(qcm_descro_row['qcm_nb'])
    valeur = nb_questions_real
    dico[cle]=valeur
    
    qcm_descro_row.update(qcm_source=dico)
    valid = True
    return valid   
        