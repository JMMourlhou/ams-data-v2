import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable           #AJOUT d'un formulaire ds table _transaction, anonyme
@anvil.tables.in_transaction
def add_1_formulaire_satisfaction(  user_stagiaire,              # users row
                                    stage_row,                   # stages row
                                    dico_rep_q_ferm,
                                    dico_rep_q_ouv,
                                    date_time
                                ):
    # Print pour vérif des 2 dicos    
    print("=============== serveur side:")
    print("============== Dict reponses fermées: ")
    print(dico_rep_q_ferm)   
    print()
    print("============== Dict reponses ouvertes: ")
    print(dico_rep_q_ouv)
    print()
    print(date_time)
    
    new_row=app_tables.stage_satisf.add_row(stage_row=stage_row,
                                            stage_type_txt=stage_row["code_txt"],
                                            stage_num_txt=str(stage_row["numero"]),
                                            date_heure=date_time,
                                            rep_dico_rep_ferm=dico_rep_q_ferm,
                                            rep_dico_rep_ouv=dico_rep_q_ouv,
                                            nom=user_stagiaire["nom"],
                                            prenom=user_stagiaire["prenom"],
                                            user_email=user_stagiaire
                                         )
    id=new_row.get_id()
    #relecture du row:
    re_read_row= app_tables.stage_satisf.get_by_id(id)
    
    if re_read_row:  
        # check de la formule de satisfaction pour que le stagiaire ne puisse pas y revenir
        row = app_tables.stagiaires_inscrits.get(   numero =     stage_row['numero'],
                                                    user_email = user_stagiaire
                                                )
        row.update(enquete_satisf=True)
    
        return(True)
    else:
        return(False)

""" -----------------------------------------------------------------------------------------------------------------------"""


@anvil.server.callable           #AJOUT d'un formulaire de suivi de stage en base ds table, non anonyme
@anvil.tables.in_transaction
def add_1_formulaire_suivi( user_stagiaire,              # users row (celui qui a rempli le formulaire)
                            stage_row,                   # stages row
                            dico_rep_q_ferm,
                            dico_rep_q_ouv,
                            date_time,
                            user_role, # S ou T ou F
                            stagiaire_du_tuteur=None  # si tuteur ou formateur a rempli, c'est le mail du stagiaire
                        ):
    # Print pour vérif des 2 dicos    
    print("=============== serveur side:")
    print("============== Dict reponses fermées: ")
    print(dico_rep_q_ferm)   
    print()
    print("============== Dict reponses ouvertes: ")
    print(dico_rep_q_ouv)
    print()
    print(date_time)
    print(user_stagiaire["email"])
    print(stage_row["code_txt"])
    new_row=app_tables.stage_suivi.add_row(
                                    user_email = user_stagiaire["email"],
                                    stage_row      = stage_row,
                                    stage_type_txt = stage_row["code_txt"],
                                    user_role           = user_role,                               # role du user  T: tuteur, S: stagiaire 
                                    stage_num_txt=str(stage_row["numero"]),
                                    date_heure=date_time,
                                    rep_dico_rep_ferm=dico_rep_q_ferm,
                                    rep_dico_rep_ouv=dico_rep_q_ouv,
                                    stagiaire_du_tuteur=stagiaire_du_tuteur
                                   )
    print("new_row",new_row)
    id=new_row.get_id()
    print(id)
    #relecture du row:
    re_read_row= app_tables.stage_suivi.get_by_id(id)
    
    if re_read_row:  
        # check sur le formulaire de suivi pour 1 tuteur ou stagiaire pour savoir s'il en a rempli un, pour affichage de ceux qui n'ont pas encore répondu
        if re_read_row:  
            # si c'est un stagiaire, j'utilise son propre stage
            if user_role == "S":
                row = app_tables.stagiaires_inscrits.get(   numero =     stage_row['numero'],
                                                            user_email = user_stagiaire
                                                        )
            if user_role == "T":
                row = app_tables.stagiaires_inscrits.get(   numero =     1003,                       # stage Tuteur 
                                                            user_email = user_stagiaire
                                                        )
            row.update(enquete_suivi=True)
        return(True)
    else:
        return(False)

# =======================================================================================================
@anvil.server.callable           #AJOUT d'un formulaire commmunication ds table com, appelé par Stage_form_com
@anvil.tables.in_transaction
def add_1_formulaire_com(  
                            stage_row, # row table stage 
                            stage_numero_txt, # num du stage en txt
                            user_row,              # user row du stagiare choisi en communication
                            nom_prenom,            # nom prenom du user
                            dico_rep_q_ferm,
                            dico_rep_q_ouv,
                            date,
                            cadre,                  # cadre de l'intervention en communication (Cours com, ...)
                            date_time
                        ):
    
    new_row=app_tables.com.add_row(stage_row=stage_row,
                                            stage_num_txt = str(stage_numero_txt),
                                            user          = user_row,
                                            nom_prenom    = nom_prenom,
                                            date          = date,              # date txt
                                            com_ferm      = dico_rep_q_ferm,
                                            com_ouv       = dico_rep_q_ouv,
                                            cadre         = cadre,
                                            date_time     = date_time
                                         )
    id=new_row.get_id()
    #relecture du row:
    re_read_row= app_tables.com.get_by_id(id)
    
    if re_read_row:  
        return(True)
    else:
        return(False)

# =======================================================================================================
@anvil.server.callable     # Sauvegarde des résultats globaux, commmunication d'un stagiaire, pour une intervention, cumul de tous les stagiaires audience, 
def add_com_results(
                         stage_row,            # stage row
                         numero,               # numero stage txt
                         user,                 # user_row
                         nom,                  # nom du stgiaire (utile pour tri)
                         date,                 # date txt 
                         pourcent_q1,          # numérique
                         pourcent_q2,
                         pourcent_q3,
                         pourcent_q4,
                         pourcent_q5,
                         pourcent_q6,
                         pourcent_q7,
                         pourcent_q8,
                         pourcent_q9,
                         pourcent_q10,
                         cadre,                  # cadre de l'intervention communication
                         q1,                     # question 1, txt
                         q2,
                         q3,
                         q4,
                         q5,
                         q6,
                         q7,
                         q8,
                         q9,
                         q10,
                         ):
    
    new_row=app_tables.com_sum.add_row(
                                        stage        = stage_row,            # stage row
                                        numero       = str(numero),               # numero stage txt
                                        user         = user,                 # user_row
                                        nom          = nom,                  # nom du stgiaire (pour tri dessus)
                                        date         = date,                 # date txt 
                                        pourcent_1  = pourcent_q1,           # numérique
                                        pourcent_2  = pourcent_q2,
                                        pourcent_3  = pourcent_q3,
                                        pourcent_4  = pourcent_q4,
                                        pourcent_5  = pourcent_q5,
                                        pourcent_6  = pourcent_q6,
                                        pourcent_7  = pourcent_q7, 
                                        pourcent_8  = pourcent_q8,
                                        pourcent_9  = pourcent_q9,
                                        pourcent_10  = pourcent_q10,
                                        cadre = cadre,                  # cadre de l'intervention communication
                                        q1 = q1,                        # question1 txt
                                        q2 = q2,                        # question1 txt
                                        q3 = q3,                        # question1 txt
                                        q4 = q4,                        # question1 txt
                                        q5 = q5,                        # question1 txt
                                        q6 = q6,                        # question1 txt
                                        q7 = q7,                        # question1 txt
                                        q8 = q8,                        # question1 txt
                                        q9 = q9,                        # question1 txt
                                        q10 = q10,                        # question1 txt
                                         )
    id=new_row.get_id()
    #relecture du row:
    re_read_row= app_tables.com_sum.get_by_id(id)
    
    if re_read_row:  
        return(True)
    else:
        return(False)