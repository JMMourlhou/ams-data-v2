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
    #print(str(stages_liste))
    # lecture des stages où le stagiaire est inscrit
    satisf = False
    suivi = False
    com = False
    qcm = False
    for stage in stages_liste:   # Si les dico des stages du user décrivants les formulaires ne sont pas vides, je peux afficher l'option dans le menu, si le stagiaire n'a pas encore effectué le formulaire
        if stage['stage']['code']['satisf_q_ferm_template'] is not None and stage['stage']['code']['satisf_q_ferm_template'] != {}:
            # si le stage est authorisé à la saisie du formulaire
            if stage['stage']['saisie_satisf_ok'] is True:
                satisf = True
        if stage['stage']['code']['suivi_stage_q_ferm_template']is not None and stage['stage']['code']['suivi_stage_q_ferm_template'] != {}:
            if stage['stage']['saisie_suivi_ok'] is True:
                suivi = True
                
        # lecture du type de stage et test si dico com est renseigné
        if stage['stage']['code']['com_ferm'] != {} and stage['stage']['code']['com_ferm'] is not None:
            com = True
            
        # lecture du type de stage et test si dico qcm est renseigné
        if stage['stage']['code']['droit_qcm'] != {} and stage['stage']['code']['droit_qcm'] is not None:
            #print(stage['stage']['code']['droit_qcm'])
            qcm = True
            
    #print('com: ', str(com))
    #print('satisf: ', str(satisf))
    #print('suivi: ', str(suivi))
    #print('qcm: ', str(qcm))
    
    return satisf, suivi, com, qcm