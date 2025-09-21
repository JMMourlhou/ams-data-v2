import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# Recherche pour le user spécifié si j'affiche formulaires com, suivi, satisf 

def test_si_formulaire(user_email):
    # historique du stagiaire
    stages_liste = app_tables.stagiaires_inscrits.search(user_email=user_email)
    # lecture des stages où le stagiaire a été inscrit
    satisf = False
    suivi = False
    for stage in stages_liste:
        if stage['enquete_satisf'] is True:
            satisf = True
        if stage['enquete_suivi'] is True:
            suivi = True
        # lecture du type de stgae et test si dico com est renseigné
        if stage['stage']['code']['com_ferm'] != None:
            