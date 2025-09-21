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
    for stage in stages_liste:   # Si les dico des stgages du user décrivants les formulaires ne sont pas vides, je peux afficher l'option dans le menu, si le stagiaire n'a pas encore effectué le formulaire
        if stage['stage']['code']['satisf_q_ferm_template'] is not None or stage['stage']['code']['satisf_q_ferm_template'] != {}:
            # si le stagiaire n'a pas encore effectué le formulaire
            if stage['enquete_satisf'] is False:
                satisf = True
        if stage['stage']['code']['suivi_stage_q_ferm_template'] is not None or stage['stage']['code']['suivi_stage_q_ferm_template'] != {}:
            if stage['enquete_suivi'] is False:
                suivi = True
        # lecture du type de stage et test si dico com est renseigné
        if stage['stage']['code']['com_ferm'] is not None or stage['stage']['code']['com_ferm'] != {}:
            com = True
        if stage['stage']['code']['droit_qcm'] is not None or stage['stage']['code']['droit_qcm'] != {}:
            qcm = True
    print('com: ', str(com))
    print('satisf: ', str(satisf))
    print('suivi: ', str(suivi))
    print('qcm: ', str(qcm))
    
    return satisf, suivi, com, qcm