import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *

#boucle sur la table old_stagiares pour modif rapide d'une colonne, ici sur la col typr de mail
def loop_old_mails():
    table_old = app_tables.stagiaires_histo.search()
    result="erreur"
    if table_old:
        for row in table_old:
            row.update(type_mail="old_pse")
        result="loop ok"     
    return result

#boucle sur la table users pour modif rapide d'une colonne, ici sur le role (sauf l'administrateur)
def loop_users():
    table_users = app_tables.users.search()
    result="erreur"
    if table_users:
        for row in table_users:
            if row['email'] != "jmarc@jmm-formation-et-services.fr":
                row.update(role="S")
        result="loop ok"     
    return result

#boucle sur la table stagiaires inscrits pour maj des droits aux qcm par type de stage
def loop_stagiaire_inscrits():
    # 1 loop sur fichier stagiaires inscrits
    liste_st_inscrits = app_tables.stagiaires_inscrits.search()
    for row_stagiaire in liste_st_inscrits:
        # 2 lecture fichier père stage
        stage_row = app_tables.stages.get(numero = row_stagiaire['stage']['numero'])    # acquisition du num de stage
        print(stage_row['numero'])
        # 3 lecture fichier père type_stage
        type_stage_row = app_tables.codes_stages.get(code = stage_row['code']['code'])
        print(type_stage_row['droit_qcm'])
        #  *************************************************************************** MAJ des droits de ce stagiaire aux qcm (par type de stage) 
        row_stagiaire.update(droits_stagiaire_qcms=type_stage_row['droit_qcm'])

#boucle sur la table qcm pour l'effacmt des question du QCM #5 
def loop_del_qcm5():
    qcm5 = app_tables.qcm_description.get(qcm_nb=5)
    liste = app_tables.qcm.search(
                                   qcm_nb=qcm5 
                                 )
    print(len(liste))
    result="erreur"
    if liste: 
        for row in liste:
            row.delete()
        result="loop ok" 
    return result



#boucle sur la table qcm_result pour l'effacmt de tous les résultats, 
def loop_del_result():
    table = app_tables.qcm_result.search()
    print(len(table))
    result="erreur"
    if table: 
        for row in table:
            row.delete()
        result="loop ok" 
    return result

#boucle sur la table qcm_result pour l'effacmt des lignes du qcm test (3), 
def loop_del_qcm3_result():
    #lecture user
    user_jm = app_tables.users.get(email="jmmourlhou@gmail.com")
    print(user_jm['prenom'])
    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=3)
    print(qcm_row['destination'])
    if qcm_row:
        table = app_tables.qcm_result.search(qcm_number=qcm_row,
                                             user_qcm=user_jm
                                            )
        print(len(table))
        result="erreur"
        if table: 
            for row in table:
                row.delete()
            result="loop ok" 
    return result

#boucle sur la table qcm pour modif rapide d'une colonne, ici sur la description
def loop_qcm19():
    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=19)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row)
        result="erreur"
        if table:
            for row in table:
                row.update(param = "Communication")
            result="loop ok"     

#boucle sur la table qcm pour modif rapide d'une colonne, ici sur le type des qcm BNSSA (4 à 9) 
def loop_qcm4():
    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=4)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row )
        result="erreur"
        txt="PSE2"
        if table:
            for row in table:
                row.update(type= "Multi"
                          )
            result="loop ok"
        print(f"loop sur qcm4: {result}")
    
    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=5)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row )
        result="erreur"
        txt="PSE2"
        if table:
            for row in table:
                row.update(type= "Multi"
                          )
            result="loop ok"
        print(f"loop sur qcm5: {result}")

    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=6)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row )
        result="erreur"
        txt="PSE2"
        if table:
            for row in table:
                row.update(type= "Multi"
                          )
            result="loop ok"
        print(f"loop sur qcm6: {result}")

    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=7)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row )
        result="erreur"
        txt="PSE2"
        if table:
            for row in table:
                row.update(type= "Multi"
                          )
            result="loop ok"
        print(f"loop sur qcm7: {result}")

    #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=8)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row )
        result="erreur"
        txt="PSE2"
        if table:
            for row in table:
                row.update(type= "Multi"
                          )
            result="loop ok"
        print(f"loop sur qcm8: {result}")

     #lecture fichier père qcm descro
    qcm_row = app_tables.qcm_description.get(qcm_nb=9)
    if qcm_row:
        table = app_tables.qcm.search(qcm_nb=qcm_row )
        result="erreur"
        txt="PSE2"
        if table:
            for row in table:
                row.update(type= "Multi"
                          )
            result="loop ok"
        print(f"loop sur qcm9: {result}")

#boucle sur la table pré-requis par stagiaire pour ajouter un pré-requiq à tous les stagiaires d'un stage
def ajout_pre_requis():
    # lecture stage 
    stage_row=app_tables.stages.get(numero=116)
    # lecture pré-requis
    pre_requis_row=app_tables.pre_requis.get(code_pre_requis="PH-DI")
    # loop sur chaque stgiaire et ajout du pré-requis
    
    stagiaires = app_tables.stagiaires_inscrits.search(stage=stage_row)
    for stagiaire in stagiaires:
        
        app_tables.pre_requis_stagiaire.add_row(
                              stage_num = stage_row,  
                              stagiaire_email = stagiaire['user_email'],
                              item_requis = pre_requis_row,
                              check=False
                )    
        print(stagiaire['user_email'], " ", pre_requis_row['code_pre_requis'])

#boucle sur la table pré-requis par stagiaire pour enlever un pré-requiq à tous les stagiaires d'un stage
def del_pre_requis():
    # lecture stage 
    stage_row=app_tables.stages.get(numero=116)
    # lecture pré-requis
    pre_requis_row=app_tables.pre_requis.get(code_pre_requis="PH-CTF-P4")
    # loop sur table pre_requis_stagiaire et del du pré-requis
    liste_a_enlever = app_tables.pre_requis_stagiaire.search(item_requis=pre_requis_row,
                                                             stage_num=stage_row
                                                            )
    for pr in liste_a_enlever:
        print(pr['stagiaire_email']," ",pr['item_requis'])
        pr.delete()

#boucle sur la table stage pour mettre  en clair (txt) le type de stage (ex PSC1) 
def maj_stages_txt():
    liste = app_tables.stages.search()
    for stage in liste:
        #lecture fichier père type stage
        row_stage = app_tables.codes_stages.get(code=stage['code']['code'])
        stage.update(code_txt=row_stage['code'])
        print(stage['numero'], stage['code_txt'])


#boucle sur la table QCM results pour nom/prenom en clair txt 
def maj_qcm_results_txt():
    # liste des résultats
    liste_results = app_tables.qcm_result.search()
    for row in liste_results:
        #lecture fichier père 'users'
        usr = app_tables.users.get(q.fetch_only("nom","prenom"),
                                        email = row['user_qcm']['email']
                                  )
        #lecture fichier père QCM_descro
        qcm = app_tables.qcm_description.get(qcm_nb=row['qcm_number']['qcm_nb'])             
        row.update(name = usr['nom'],
                  prenom = usr['prenom'],
                   intitule= qcm['destination']
                  )

#boucle sur la table QCM results pour effact qcm essai
def del_qcm_results_essai():
    nb_del = 0
    # liste des résulltats
    #lecture table qcm mère QCM _desro sur qcm 3
    row_essai = app_tables.qcm_description.get(qcm_nb=3)  # qcm-nb int
    # liste des qcm d'essai
    liste_results = app_tables.qcm_result.search(
                                                    qcm_number=row_essai
                                                )
    for row in liste_results:
        nb_del += 1
        row.delete()
    result = (f"{nb_del} qcm effacés")
    return result


#boucle sur la table QCM results pour effact qcm de plus de 2 mois, échoués
def del_qcm_results_unsuccessed_old():
    from . import French_zone
    from datetime import datetime, timedelta

    nb_del = 0
    # liste des qcm results
    liste_results = app_tables.qcm_result.search()
    for row in liste_results:
        diff = French_zone.time_diff(row['time'])
        print(f"diff: {timedelta.total_seconds(diff)} seconds")
        
        diff_in_seconds = int(timedelta.total_seconds(diff))
        one_day_in_seconds = 60 * 60  * 24  # 86400 sec / day
        two_months_in_seconds = one_day_in_seconds * 60
        
        days = int(timedelta.total_seconds(diff)) / one_day_in_seconds
        print(f"diff: {days} days")          
        if row['success'] is False and diff_in_seconds > two_months_in_seconds:     # plus de 2 mois, échoués
            nb_del += 1
            print(f"diff: {days} days, {row['success']}, effact")
            row.delete()
    
    result = (f"{nb_del} qcm effacés")
    return result
        
        