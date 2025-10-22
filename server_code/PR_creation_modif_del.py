import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import *  #pour les alertes

#Création d'un nouveau Pré-Requis
@anvil.server.callable 
def add_pr(code, intitule, commentaires):
    
    new_row=app_tables.pre_requis.add_row(
                              code_pre_requis=code,
                              requis=intitule,
                              commentaires=commentaires,
                              doc=False
                             )
                 
    pr = app_tables.pre_requis.search(code_pre_requis=new_row['code_pre_requis'])
    if len(pr)>0:
        valid=True
    else:
        valid=False
    return valid


# ==========================================================================================
@anvil.server.callable           #modif d'un intitulé pr et répercution ds la table pr_stgiaires ET Table Codes_stages, si le dictionnaire des pr pour un stage contient ce code
def modif_pr(pr_row, intitule, code, commentaire, old_code):
    valid = False
    pr_row.update(requis = intitule,
                 code_pre_requis = code,
                 commentaires = commentaire)
    
    # modif du PR existant en table "pre_requis_stagiaire"
    liste = app_tables.pre_requis_stagiaire.search(item_requis=pr_row)
    if len(liste)>0:
        for pr_r in liste:
            pr_r.update(requis_txt = intitule)
            
    # modif des PR existants en table Codes_stages
    liste = app_tables.codes_stages.search()   # lecture de chaque stage
    for stage in liste:
        # lecture du dico
        dico = {}
        dico = stage['pre_requis']
        # recherche si clef (old_code) existante, si oui effact ancienne clef puis recréation avec la nouvelle
        try:
            test = dico.get(old_code)
            if test is not None: # Clé existante 1 on l'efface, 2 on recrée 
                del dico[old_code]
                # création du nx pr ds dico pr pour ce stage
                clef = code
                valeur = {                                 # AJOUT DE LA nouvelle CLEF DS LE DICO PR table codes stages
                                "Doc": "",
                                "Validé": False,
                                "Commentaires": "new",
                                "Nom_document": ""
                }
                dico[clef]= valeur
                # réécriture du row stage
                stage.update(pre_requis=dico)
        except:
            pass
        valid=True
    return valid, len(liste)

# ==========================================================================================
@anvil.server.callable           #Del d'un pr et répercution ds la table pr_stgiaires ET table code_stages
def del_pr(pr_row, code):
    valid = False
    valid1 = False
    valid2 = False
    pr_row.delete()

    
    # del des PR stagiaires existants
    liste = app_tables.pre_requis_stagiaire.search(item_requis=pr_row)
    if len(liste)>0:
        for pr_r in liste:
            pr_r.delete()
            valid1 = True
        # Vérification
        liste1 = app_tables.pre_requis_stagiaire.search(item_requis=pr_row)
        if len(liste1)==0:
            valid2 = True

    # del des PR existants en table Codes_stages (s'il y en a ! )
    liste = app_tables.codes_stages.search()   # lecture de chaque stage
    for stage in liste:
        # lecture du dico
        dico = {}
        dico = stage['pre_requis']
        # recherche si clef (old_code) existante, si oui effact ancienne clef puis recréation avec la nouvelle
        test = dico.get(code)
        if test is not None: # Clé existante 1 on l'efface
            del dico[code]
            # réécriture du row stage sans la clef
            stage.update(pre_requis=dico)
            
    if valid1 is True and valid2 is True:
        valid=True
    return valid, len(liste)
