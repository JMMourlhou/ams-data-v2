import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *

# Recherche pour le user spécifié si j'affiche dans main formulaires com, suivi, satisf 

def test_si_formulaire(user_email):
    # historique du stagiaire
    stages_liste = app_tables.stagiaires_inscrits.search(user_email=user_email)
    print(list(stages_liste))
    # lecture des stages où le stagiaire est inscrit
    satisf = False
    suivi = False
    com = False
    qcm = False
    for stage in stages_liste:
        if stage['enquete_satisf'] is True:
            satisf = True
        if stage['enquete_suivi'] is True:
            suivi = True
        # lecture du type de stgae et test si dico com est renseigné
        if stage['stage']['code']['com_ferm'] is not None or stage['stage']['code']['com_ferm'] != {}:
            com = True
        if stage['stage']['code']['droit_qcm'] is not None or stage['stage']['code']['droit_qcm'] != {}:
            qcm = True
    print('com: ', str(com))
    print('satisf: ', str(satisf))
    print('suivi: ', str(suivi))
    print('qcm: ', str(qcm))
    
    return satisf, suivi, com, qcm