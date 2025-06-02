import anvil.email
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import anvil.files
from anvil.files import data_files

"""
**************************************************** LECTURE FICHIER CSV EN BGT 
"""
@anvil.server.background_task
def csv_file_reader(csv_file):
    f = open(data_files[csv_file.name])    # csv_file est : file du file loader. RAJOUTER .name ici pour obtenir on nom
    x = True
    nb = 0 # Nb de mails ajoutés
    print("Ouverture du fichier")
    while x:
        ligne = []
        text=f.readline()  # lecture  1 ligne
        if not text:                                        # FIN DE FICHIER TEXT           #rep = rep + dernier_caract
            print('Fin du fichier')
            return('Fin du fichier',nb)
        
        # création d'une liste, à partir du séparateur ";" (CSV file)
        ligne = text.split(';')
        
        #extraction d'1 fichier créé pour INFO COLL 
        type_mail=ligne[0]           # extraction du type de mail ex: 
        nom=ligne[1]                 # extraction date du diplome
        prenom=ligne[2]              # extraction du nom
        mail=ligne[3]                # extraction du prenom
        
        
        """
        extraction de l'extranet FNMNS
        num=ligne[0]           # extraction du num ligne excel
        date_diplome=ligne[1]  # extraction date du diplome
        nom=ligne[2]           # extraction du nom
        prenom=ligne[3]        # extraction du prenom
        date_naissance=ligne[4]  # extraction date N
        lieu_naissance=ligne[5]  # extraction lieu N
        rue=ligne[6]             # extraction rue
        cp=ligne[7]             # extraction cp
        ville=ligne[8]          # extraction ville
        tel=ligne[9]            # extraction du tel
        mail=ligne[10]          # extraction du mail
        """
        # je recherche si un doublon existe déjà
        row = app_tables.stagiaires_histo.get(mail=mail)
        if not row:                             # mail innexistant, je l'ajoute                   
            nb += 1
            app_tables.stagiaires_histo.add_row(mail=mail,
                                                type_mail=type_mail,
                                                nom=nom,
                                                prenom=prenom,
                                                
                                                tel=None,
                                                num=None,
                                                date_diplome=None,                                              
                                                date_n=None,
                                                lieu_n=None,
                                                rue=None,
                                                ville=None,
                                                cp=None
                                            )

@anvil.server.callable
def run_bg_task_csv_reader(csv_file):
    task = anvil.server.launch_background_task('csv_file_reader',csv_file)
    return task

"""
**************************************************************** FIN DU PRECESSUS BGT
"""




# MAJ du l'envoi à partir de Mai_to_old_stagiaires (Coche Envoi a changé)
@anvil.server.callable
def maj_histo_envoi(item, envoi):   # item de l'enregistrement d'un ancien stagiare 
    item.update(envoi=envoi)
    return True

# del d'une row d'un ancien stgiaire  à partir de  Mai_to_old_stagiaires
@anvil.server.callable
def del_histo(item):   # item de l'enregistrement d'un ancien stagiare 
    item.delete()
    return True

# MAJ de la sélection à partir de Mail_to_old_stagiaires (Coche Envoi a changé)
@anvil.server.callable
def maj_selection(item, select, nb):   # item de l'enregistrement d'un ancien stagiare 
    if select is True:
        nb += 1
    else:
        nb -= 1
    item.update(select=select)
    return True, nb