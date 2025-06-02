import anvil.email

import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

#boucle sur la table stagiaire inscrits pour  en clair txt Nom Prénom (1ere lettre en majuscule) et num stage
@anvil.server.callable
def maj_stagiaires_inscrits_txt():
    liste_stagiaires = app_tables.stagiaires_inscrits.search()
    for row in liste_stagiaires:
        #lecture fichier père 'users'
        usr = app_tables.users.get(q.fetch_only("nom", "prenom"),
                                        email = row['user_email']['email']
                                  )
        # lecture du nom et capitalize le nom
        n = usr['nom']
        n = n.capitalize()
        n = n.strip()
        # lecture du nom et capitalize le nom
        p = usr['prenom']
        p = p.capitalize()
        p = p.strip()
        row.update(
                    name = n,
                    prenom = p
                  )

#================================================================================================================
# EN BG TASK
#boucle sur toute la table pre_requis_stagiaire pour maj colonnes nom, prenom, numero, pr en clair txt 
# et effact de pr si le user n'existe plus
@anvil.server.background_task
def maj_pr_stagiaires_txt():
    # Drop down stages inscrits du user
    liste_pr_stagiaires = app_tables.pre_requis_stagiaire.search()
    
    for row in liste_pr_stagiaires:
        #lecture fichier père stage
        stage = app_tables.stages.get(q.fetch_only("date_debut"),
                                                    numero=row['stage_num']['numero']
                                    )
        print(f"Traitement du stage {stage['code_txt']}")
        #lecture fichier père pré_requis
        pr = app_tables.pre_requis.get(code_pre_requis=row['item_requis']['code_pre_requis'])
        #lecture fichier père user
        try:
            usr = app_tables.users.get(email=row['stagiaire_email']['email'])
            row.update(code_txt=stage['code_txt'],
                  numero=stage['numero'],
                  nom=usr['nom'],
                  prenom=usr['prenom'],
                  requis_txt=pr['requis'])
        except:   # si user non trouvé, effact des pré requis
            print("row deleted for: ", row['stagiaire_email'])
            row.delete()

@anvil.server.callable
def run_bg_task_maj_pr_stagiaires_txt():
    task = anvil.server.launch_background_task('maj_pr_stagiaires_txt')
    return task
