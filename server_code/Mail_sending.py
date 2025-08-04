from anvil import *
import anvil.email
import anvil.files
from anvil.files import data_files
import tables
from tables import app_tables
import anvil.users
import anvil.server
from anvil.http import url_encode

from . import French_zone_server_side
from . import Variables_globales # importation du module de lecture des variables globales (de la table Variables_globales) 


"""Send an email to the specified user"""
"""
**************************************************** LECTURE FICHIER CSV EN BGT 
"""
@anvil.server.background_task
def send_mail(emails_list, subject_txt, rich_text, old_stagiaires=False, attachments=[]):
    
    # Initialisation du nb de mails envoyés
    nb_mails = 0
    # Récupération des variables globales
    dict_var_glob = Variables_globales.get_variable_names()   # var_globale du mail d'AMS, stockées ds table 
    client_mail = dict_var_glob["ams_mail"]   # var globale Mail AMS
    code_app1 = dict_var_glob["code_app1"]      # var_globale de l'apli AMS DATA
    en_tete_address = code_app1+"/_/theme/"+ dict_var_glob["ams_en_tete"]
    # ------------------------------------------
    fin_mail_carte = code_app1+"/_/theme/"+ dict_var_glob["ams_carte"]
    fin_mail_qualiopi = code_app1+"/_/theme/"+ dict_var_glob["qualiopi_logo"]
    # ------------------------------------------
    # Tps début de traitement
    time_deb=French_zone_server_side.time_french_zone() # time is a datetime format 
    for email, prenom, id in emails_list:
        # time début de traitement
        time=French_zone_server_side.time_french_zone() # time is a datetime format 
        print(time)
        try:
            anvil.email.send(
                to=email,
                from_address = "amsport@amsdata.org",
                from_name = "AMSport",
                subject=subject_txt,
                attachments=attachments,
                html=f"""
                    <p><img src = {en_tete_address} width="772" height="263"> </p>
                    <b>{prenom},</b><br>
                    <br>
                    {rich_text} <br>
                    <span>Contacter AMSport: {client_mail}</span> 
                    <p><img src = {fin_mail_carte} width="370" height="236"> </p>
                    <br>
                    <p><img src = {fin_mail_qualiopi} width="150" height="100"> 
                """
            )
            nb_mails += 1 # incrément nb de mails envoyés
            
            # sauve le nb de mails ds table temp
            table_temp = app_tables.temp.search()[0]
            table_temp.update(nb_mails_sent=nb_mails)
            
            if old_stagiaires is True:
                # sauver la date et l'heure
                row_old_stagiaire = app_tables.stagiaires_histo.get_by_id(id)
                if row_old_stagiaire:
                    row_old_stagiaire.update(envoi=True, Date_time_envoi=time, select=False)
                    #print(row_old_stagiaire['mail'], "envoyé pour", prenom)
                else:
                    print(row_old_stagiaire['mail'], "row non trouvé en maj")
                    
            # Log du mail envoyé
            fichiers_txt = ""
            if attachments != []:
                for file in attachments:
                    fichiers_txt = fichiers_txt + str(file.name) +" , "
                
            app_tables.mails_histo.add_row(
                                            date_heure=time, # time is a datetime format ,
                                            mail=email,
                                            objet=subject_txt,
                                            fichiers_attachés=fichiers_txt
                                            )
        except Exception as e:
            print("Une exception a été déclenchée :", e)
            if old_stagiaires is True:
                # sauver l'erreur
                row_old_stagiaire = app_tables.stagiaires_histo.get_by_id(id)
                row_old_stagiaire.update(envoi=False, erreur_mail=True)
                
        # possible de changer la couleur d'un texte:   <b><p style="color:blue;"> {user_row["prenom"]}, </p></b>
    
    # Tps fin de traitement
    time_fin=French_zone_server_side.time_french_zone() # time is a datetime format 
    # Durée de traitement
    time_traitement = time_fin - time_deb
    print(f"durée du traitement: {time_traitement} pour envoyer {nb_mails} mails")


@anvil.server.callable
def run_bg_task_mail(emails_list, subject_txt, rich_text, attachments=[], old_stagiaires=False):
    print("old_stagiaires 1",old_stagiaires)
    task = anvil.server.launch_background_task('send_mail',emails_list, subject_txt, rich_text, old_stagiaires,attachments)
    return task
    
    """
    **************************************************************** FIN DU PROCESSUS BGT
    """