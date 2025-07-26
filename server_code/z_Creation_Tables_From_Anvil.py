import anvil.server
from anvil.tables import app_tables
#from uplink_2 import run_uplink_2


# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def copy_tables_from_anvil():
    #!/usr/bin/env python3

    # écrit par JMM le 08/0/2025
    # Ce script python est le uplink de pi5 (serveur) vers l'application développement @ anvil
    # il permettra la lecture de la varible rows par l'application jmmweb sur pi5 et l'installation de la table 'produits'

    # -------------  IMPORTANT  -------------------------------------------------------------------------------------------
    # ce script python doit être placé ds le rep /home/jmsite/up_link.py pour être lu par l'appli anvil sur pi5
    # ---------------------------------------------------------------------------------------------------------------------
    
    # Connexion chez Anvil-works pour lecture des fichiers 
    
    # PRINCIPE IMPORTANT:
    # Lors de la première itération, l’itérateur fait un appel Uplink et pré-charge les 100 premiers row_ids.
    # Pour la 101ᵉ ligne, il doit émettre un nouvel appel Uplink (next_page) pour rapatrier les IDs des lignes 101–200.
    # Si tu as déjà fermé (disconnect()) ou reconnecté sur un autre serveur avant ce 101ᵉ appel, la WebSocket n’existe plus :
    # next_page échoue → Connection lost
    # L’itérateur, privé de sa liste de _row_ids, déclenche un IndexError: list index out of range.
    
    # Il faut donc transformer l’itérateur en vraie liste avant de couper la connexion :
    # Exemple    rows_users_distant = list(app_tables.users.search())
    
    
   
    anvil.server.connect("server_RTZBJFVVIHPARCDIOYGH77Z3-SXGQVEYU3C2NJ5KR")   # code up link pour les bases amsdata.org chez Anvil-works
    
    
    # ------------------------------------------------------------------------Fichier cpt_stages
    rows_cpt_stages_distant = list(app_tables.cpt_stages.search())
    print(f"nb de rows fichier cpt_stages: {len(rows_cpt_stages_distant)}")
    
    # -----------------------------------------------------------------------Fichier users
    rows_users_distant = list(app_tables.users.search())
    print(f"nb de rows fichier users: {len(rows_users_distant)}")
    
    # -----------------------------------------------------------------------Fichier Mode fi
    rows_mode_fi_distant = list(app_tables.mode_financement.search())
    print(f"nb de rows fichier mode_fi: {len(rows_mode_fi_distant)}")
    
    # -----------------------------------------------------------------------Fichier Codes stages
    rows_code_stages_distant = list(app_tables.codes_stages.search())
    print(f"nb de rows fichier code stages: {len(rows_code_stages_distant)}")
    
    # -----------------------------------------------------------------------Fichier lieux
    rows_lieux_distant = list(app_tables.lieux.search())
    print(f"nb de rows fichier lieux: {len(rows_lieux_distant)}")
    
    # -----------------------------------------------------------------------Fichier event_types
    rows_event_types_distant = list(app_tables.event_types.search())
    print(f"nb de rows fichier event_types: {len(rows_event_types_distant)}")
    
    # -----------------------------------------------------------------------Fichier mail_type
    rows_mail_type_distant = list(app_tables.mail_type.search())
    print(f"nb de rows fichier mail_type: {len(rows_mail_type_distant)}")
    
    # -----------------------------------------------------------------------Fichier mails_histo
    rows_mails_histo_distant = list(app_tables.mails_histo.search())
    print(f"nb de rows fichier mails_histo: {len(rows_mails_histo_distant)}")
    
    # -----------------------------------------------------------------------Fichier pre_requis
    rows_pre_requis_distant = list(app_tables.pre_requis.search())
    print(f"nb de rows fichier pre_requis: {len(rows_pre_requis_distant)}")
    
    # -----------------------------------------------------------------------Fichier texte_formulaires
    rows_texte_formulaires_distant = list(app_tables.texte_formulaires.search())
    print(f"nb de rows fichier texte_formulaires: {len(rows_texte_formulaires_distant)}")
    
    # -----------------------------------------------------------------------Fichier texte_formulaires
    rows_global_variables_distant = list(app_tables.global_variables.search())
    print(f"nb de rows fichier global_variables: {len(rows_global_variables_distant)}")
    
    # -----------------------------------------------------------------------Fichier stagiaires_histo
    rows_stagiaires_histo_distant = list(app_tables.stagiaires_histo.search())
    print(f"nb de rows fichier stagiaires_histo: {len(rows_stagiaires_histo_distant)}")
    
    # ------------------------------------------------------------------------Fichier files
    rows_files_distant = list(app_tables.files.search())
    print(f"nb de rows fichier files: {len(rows_files_distant)}")
    
    # ------------------------------------------------------------------------Fichier temp
    rows_temp_distant = list(app_tables.temp.search())
    print(f"nb de rows fichier temp: {len(rows_temp_distant)}")
    
    
    # --------------------------------------------------------------------------------------------DECONNECTION de la base amsdata chez Anvil-works
    anvil.server.disconnect()
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  ECRITURE base amsdata SUR Pi5
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    
    # connection au serveur Anvil local Pi5 par up link
    # mettre en secret (Cette clé est ds le config file anvil app jmmweb-config-file.yaml)
    
    # A CHANGER SI JE PASSE EN HTTPS !!!!!!!!!!
    # Ici, j'utilise ws et pas wss car serveur Anvil local ne fait que du HTTP/WS (pas de certificat TLS)
    # anvil.server.connect("amsdata-up-link-9f497ae69de039517b9b89a0fdbdfb6246a61e6de190d873b3dd1496356bc49f", url="ws://192.168.1.250:8080/_/uplink")
    
    # connection à amsdata v2 sur Pi5, https, domaine clouflare sur le config file
    anvil.server.connect("amsdata-up-link-9f497ae69de039517b9b89a0fdbdfb6246a61e6de190d873b3dd1496356bc49f",url="wss://www.jmweb34.net/_/uplink")    # amsdata v2 sur Pi5, domaine clouflare sur le config file
    # ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------ Table USERS 
    # -----------------------------------------------------------------------------------------
    # 1- Réinitialisation table USERS par effacement des rows existantes éventuelles:
    try:
        app_tables.users.delete_all_rows()
        print("Toutes les rows des users ont été effacées")
    except Exception as e:
        print(f"❌ Erreur lors de l'effacement de la table users : {e}")
    
    
    # ------------------------------------------------------------------------------------------
    # 2- ECRITURE des rows table USERS:
    print("Ecriture des rows du fichier distant 'users'")
    
    
    cpt = 0
    for row_distant in rows_users_distant:    
        try:
            app_tables.users.add_row(
                email                    = row_distant['email'],
                role                     = row_distant['role'],
                enabled                  = row_distant['enabled'],
                signed_up                = row_distant['signed_up'],
                last_login               = row_distant['last_login'],
                nom                      = row_distant['nom'],
                prenom                   = row_distant['prenom'],
                password_hash            = row_distant['password_hash'],
                api_key                  = row_distant['api_key'],
                n_password_failures      = row_distant['n_password_failures'],
                confirmed_email          = row_distant['confirmed_email'],
                date_naissance           = row_distant['date_naissance'],
                ville_naissance          = row_distant['ville_naissance'],
                code_postal_naissance    = row_distant['code_postal_naissance'],
                pays_naissance           = row_distant['pays_naissance'],
                adresse_rue              = row_distant['adresse_rue'],
                adresse_ville            = row_distant['adresse_ville'],
                adresse_code_postal      = row_distant['adresse_code_postal'],
                tel                      = row_distant['tel'],
                email2                   = row_distant['email2'],
                commentaires             = row_distant['commentaires'],
                accept_data              = row_distant['accept_data'],
                temp                     = row_distant['temp'],
                temp2                    = row_distant['temp2'],
                temp3                    = row_distant['temp3'],
                temp_for_stage           = row_distant['temp_for_stage'],
                                        dico_menu                = row_distant['dico_menu'],
                                                                    )
            cpt += 1
            print(f"✅' 'row {cpt} insérée pour {row_distant['nom']}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table users, nom: {row_distant['nom']})) : {e}")
    print("Fin du traitement USERS")
    print("")
    
    
    # ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------ Table cpt_stages
    # -----------------------------------------------------------------------------------------
    # 1- Réinitialisation table cpt_stages par effacement des rows existantes éventuelles:
    rows_local = list(app_tables.cpt_stages.search())
    nb_local = len(rows_local)
    
    
    for row in rows_local:
        try:                  # effacement
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table cpt_stages ) : {e}")
    print(f"{nb_local} rows cpt_stages éffacée(s)")     
    
    
    # ------------------------------------------------------------------------------------------
    # 2- ECRITURE des rows table cpt_stages:
    print(f"Ecriture des rows du fichier distant 'cpt_stages'")
    
    cpt = 0
    for row_distant in rows_cpt_stages_distant:    
        try:
            app_tables.cpt_stages.add_row( compteur = row_distant['compteur'] )
            cpt += 1
            print(f"✅' 'row {cpt} insérée pour {row_distant['compteur']}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table cpt_stages, nom: {row_distant['compteur']})) : {e}")
    
    print("Fin du traitement CPT_STAGES")
    print("")
    # ------------------------------------------------------------------ Table mode_fi
    # -----------------------------------------------------------------------------------------
    # 1- Réinitialisation table mode_fi par effacement des rows existantes éventuelles:
    rows_local = list(app_tables.mode_financement.search())
    nb_local = len(rows_local)
    
    
    for row in rows_local:
        try:                  # effacement
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table mode_fi ) : {e}")
    print(f"{nb_local} rows mode_fi éffacée(s)")     
    
    
    # ------------------------------------------------------------------------------------------
    # 2- ECRITURE des rows table mode_fi:
    print(f"Ecriture des rows du fichier distant 'mode_financement'")
    #anvil.server.connect("amsdata-up-link-4bd1df5861ca73a959def81e8caaf84c3eabcab1f317ba402062d915b26be9cb", url="ws://192.168.1.250:8080/_/uplink")
    
    cpt = 0
    for row_distant in rows_mode_fi_distant:    
        try:
            app_tables.mode_financement.add_row(
                                                    code_fi     = row_distant['code_fi'],
                                                    intitule_fi = row_distant['intitule_fi'],
                                                )
            cpt += 1
            print(f"✅' 'row {cpt} insérée pour {row_distant['code_fi']}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table mode_fi, nom: {row_distant['code_fi']})) : {e}")
    # anvil.server.disconnect()
    print("Fin du traitement MODE Fi")
    print("")
    # ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------ Table codes stages
    # -----------------------------------------------------------------------------------------
    # 1- Réinitialisation table codes stages par effacement des rows existantes éventuelles:
    rows_local = list(app_tables.codes_stages.search())
    nb_local = len(rows_local)
    
    
    for row in rows_local:
        try:                  # effacement
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table codes stages ) : {e}")
    print(f"{nb_local} rows codes stages éffacée(s)")     
    
    # print("Serveur Anvil local déconnecté correctement après effacement")
    
    # ------------------------------------------------------------------------------------------
    # 2- ECRITURE des rows table codes stages:
    print(f"Ecriture des rows du fichier distant 'codes stages'")
    #anvil.server.connect("amsdata-up-link-4bd1df5861ca73a959def81e8caaf84c3eabcab1f317ba402062d915b26be9cb", url="ws://192.168.1.250:8080/_/uplink")
    
    cpt = 0
    for row_distant in rows_code_stages_distant:    
        try:
            app_tables.codes_stages.add_row(
            code                             = row_distant['code'],
            intitulé                         = row_distant['intitulé'],
            pre_requis                       = row_distant['pre_requis'],
            droit_qcm                        = row_distant['droit_qcm'],
            satisf_q_ferm_template          = row_distant['satisf_q_ferm_template'],
            satisf_q_ouv_template           = row_distant['satisf_q_ouv_template'],
            suivi_stage_q_ferm_template     = row_distant['suivi_stage_q_ferm_template'],
            suivi_stage_q_ouv_template      = row_distant['suivi_stage_q_ouv_template'],
            type_stage                       = row_distant['type_stage'],
            com_ouv                          = row_distant['com_ouv'],
            com_ferm                         = row_distant['com_ferm'],
            dico_menu                        = row_distant['dico_menu'],
        )
            cpt += 1
            print(f"✅' 'row {cpt} insérée pour {row_distant['code']}, {row_distant['pre_requis']}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table codes stages, nom: {row_distant['code']} : {e}")
    
    print("Fin du traitement codes_stages")
    print("")
    # -----------------------------------------------------------------------------------------------------
    #                                                                                          Table: lieux
    # ----------------------------------------
    # 1- Réinitialisation table lieux par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.lieux.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table lieux : {e}")
    print(f"{nb_local} rows lieux effacée(s)")
    
    # ----------------------------------------
    # 2- ÉCRITURE des rows table lieux :
    print("Ecriture des rows du fichier distant 'lieux'")
    cpt = 0
    for row_distant in rows_lieux_distant:
        try:
            app_tables.lieux.add_row(
                lieu      = row_distant['lieu'],
                adresse   = row_distant['adresse'],
                remarques = row_distant['remarques'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour {row_distant['lieu']}")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table lieux, lieu: {row_distant['lieu']}) : {e}")
    
    print("Fin du traitement lieux")
    print("")
    # -----------------------------------------------------------------------------------------------------
    #                                                                                     Table: event_types
    # ----------------------------------------
    # 1- Réinitialisation table event_types par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.event_types.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table event_types : {e}")
    print(f"{nb_local} rows event_types effacée(s)")
    
    # ------------------------------------------------------
    # 2- ÉCRITURE des rows table event_types :
    print("Ecriture des rows du fichier distant 'event_types'")
    cpt = 0
    for row_distant in rows_event_types_distant:
        try:
            app_tables.event_types.add_row(
                type           = row_distant['type'],
                msg_1          = row_distant['msg_1'],
                text_initial   = row_distant['text_initial'],
                msg_0          = row_distant['msg_0'],
                code           = row_distant['code'],
                mot_clef_setup = row_distant['mot_clef_setup'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour code {row_distant['code']}")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table event_types, code: {row_distant['code']}) : {e}")
    
    print("Fin du traitement event_types")
    print("")
    # -----------------------------------------------------------------------------------------------------
    #                                                                                      Table: mail_type
    # ----------------------------------------
    # 1- Réinitialisation table mail_type par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.mail_type.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table mail_type : {e}")
    print(f"{nb_local} rows mail_type effacée(s)")
    
    # -------------------------------------------------------------
    #  2- ÉCRITURE des rows table mail_type :
    print("Ecriture des rows du fichier distant 'mail_type'")
    cpt = 0
    for row_distant in rows_mail_type_distant:
        try:
            app_tables.mail_type.add_row(
                ref       = row_distant['ref'],
                type_mail = row_distant['type_mail'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour ref {row_distant['ref']}")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table mail_type, ref: {row_distant['ref']} : {e}")
    
    print("Fin du traitement mail_type")
    print("")
    # -----------------------------------------------------------------------------------------------------
    #                                                                                    Table: mails_histo
    # ----------------------------------------
    # 1- Réinitialisation table mails_histo par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.mails_histo.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table mails_histo : {e}")
    print(f"{nb_local} rows mails_histo effacée(s)")
    
    # ----------------------------------------------------------
    # 2- ÉCRITURE des rows table mails_histo :
    print("Ecriture des rows du fichier distant 'mails_histo'")
    cpt = 0
    for row_distant in rows_mails_histo_distant:
        try:
            app_tables.mails_histo.add_row(
                date_heure        = row_distant['date_heure'],
                mail              = row_distant['mail'],
                objet             = row_distant['objet'],
                fichiers_attachés = row_distant['fichiers_attachés'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour mail '{row_distant['mail']}' à {row_distant['date_heure']}")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table mails_histo, mail: {row_distant['mail']} : {e}")
    
    print("Fin du traitement mails_histo")
    print("")
    # -----------------------------------------------------------------------------------------------------
    #                                                                                     Table: pre_requis
    # ----------------------------------------
    # 1- Réinitialisation table pre_requis par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.pre_requis.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table pre_requis : {e}")
    print(f"{nb_local} rows pre_requis effacée(s)")
    
    # --------------------------------------------------------------
    # 2- ÉCRITURE des rows table pre_requis :
    print("Ecriture des rows du fichier distant 'pre_requis'")
    cpt = 0
    for row_distant in rows_pre_requis_distant:
        try:
            app_tables.pre_requis.add_row(
                code_pre_requis = row_distant['code_pre_requis'],
                requis          = row_distant['requis'],
                commentaires    = row_distant['commentaires'],
                doc             = row_distant['doc'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour code_pre_requis '{row_distant['code_pre_requis']}'")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table pre_requis, code_pre_requis: {row_distant['code_pre_requis']} : {e}")
    
    print("Fin du traitement pre_requis")
    print("")
    # -----------------------------------------------------------------------------------------------------
    #                                                                                table: texte_formulaires
    # ----------------------------------------
    # 1- Réinitialisation table texte_formulaires par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.texte_formulaires.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table texte_formulaires : {e}")
    print(f"{nb_local} rows texte_formulaires effacée(s)")
    
    # ----------------------------------------------------------------
    # 2- ÉCRITURE des rows table texte_formulaires :
    print("Ecriture des rows du fichier distant 'texte_formulaires'")
    cpt = 0
    for row_distant in rows_texte_formulaires_distant:
        try:
            app_tables.texte_formulaires.add_row(
                code        = row_distant['code'],
                text        = row_distant['text'],
                obligation  = row_distant['obligation'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour code '{row_distant['code']}'")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table texte_formulaires, code: {row_distant['code']} : {e}")
    
    print("Fin du traitement texte_formulaires")
    print("")
    
    # ----------------------------------------------------------------------------------------------------------
    #                                                                                    Table: global_variables
    # ----------------------------------------
    # 1- Réinitialisation table global_variables par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.global_variables.search())
    nb_local = len(rows_local)
    for row in rows_local:
        try:
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table global_variables : {e}")
    print(f"{nb_local} rows global_variables effacée(s)")
    
    # ------------------------------------------------------------------------------------------
    # 2- ÉCRITURE des rows table global_variables :
    print("Ecriture des rows du fichier distant 'global_variables'")
    cpt = 0
    for row_distant in rows_global_variables_distant:
        try:
            app_tables.global_variables.add_row(
                name         = row_distant['name'],
                value        = row_distant['value'],
                Commentaires = row_distant['Commentaires'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour name '{row_distant['name']}'")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table global_variables, name: {row_distant['name']} : {e}")
    
    print("Fin du traitement global_variables")
    print("")
    # ------------------------------------------------------------------------------------------------------------------------
    #                                                                                                  Table: stagiaires_histo
    # ----------------------------------------
    # 1- Réinitialisation table stagiaires_histo par effacement des rows existantes éventuelles :
    rows_local=list(app_tables.stagiaires_histo.search())
    nb_local = len(rows_local)
    print(f"{nb_local} rows stagiaires_histo avant effact")
    
    app_tables.stagiaires_histo.delete_all_rows()
    
    rows_local=list(app_tables.stagiaires_histo.search())
    nb_local = len(rows_local)
    print(f"{nb_local} rows stagiaires_histo après effact")
    
    # ------------------------------------------------------------------------------------------
    # 2- ÉCRITURE des rows table stagiaires_histo :
    print("Ecriture des rows du fichier distant 'stagiaires_histo'")
    cpt = 0
    for row_distant in rows_stagiaires_histo_distant:
        try:
            app_tables.stagiaires_histo.add_row(
                num            = row_distant['num'],
                mail           = row_distant['mail'],
                diplome        = row_distant['diplome'],
                lieu_diplome   = row_distant['lieu_diplome'],
                date_diplome   = row_distant['date_diplome'],
                nom            = row_distant['nom'],
                prenom         = row_distant['prenom'],
                date_n         = row_distant['date_n'],
                lieu_n         = row_distant['lieu_n'],
                rue            = row_distant['rue'],
                cp             = row_distant['cp'],
                ville          = row_distant['ville'],
                tel            = row_distant['tel'],
                envoi          = row_distant['envoi'],
                Date_time_envoi= row_distant['Date_time_envoi'],
                erreur_mail    = row_distant['erreur_mail'],
                select         = row_distant['select'],
                type_mail      = row_distant['type_mail'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour num '{row_distant['mail']}'")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table stagiaires_histo, num: {row_distant['mail']} : {e}")
    
    print("Fin du traitement stagiaires_histo")
    print("")
    
    # ------------------------------------------------------------------ Table: files
    # 1- Réinitialisation table files par effacement des rows existantes éventuelles :
    try:
        app_tables.files.delete_all_rows()
        print("Toutes les rows de files ont été effacées")
    except Exception as e:
        print(f"❌ jm Erreur lors de l'effacement de la table files : {e}")
    
    
    # ------------------------------------------------------------------------------------------
    # 2- ÉCRITURE des rows de la table files :
    print("Ecriture des rows du fichier distant 'files'")
    cpt = 0
    for row_distant in rows_files_distant:
        try:
            app_tables.files.add_row(
                path         = row_distant['path'],
                #file         = row_distant['file'],
                file_version = row_distant['file_version'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour path '{row_distant['path']}'")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de la table files, path: {row_distant['path']} : {e}")
    
    print("Fin du traitement files")
    
    print("")
    print(" ---------------------------------------------------------------------")
    print("Fin des maj des tables de base")
    
    
    print("")
    print(" ---------------------------------------------------------------------")
    
    
    # ------------------------------------------------------------------ Table: temp
    # 1- Réinitialisation table temp par effacement des rows existantes éventuelles :
    rows_local = list(app_tables.temp.search())
    nb_local = len(rows_local)
    
    for row in rows_local:
        try:                  # effacement
            row.delete()
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement de la table temp : {e}")
        print(f"{nb_local} rows temp effacée(s)")
    
    # ------------------------------------------------------------------------------------------
    # 2- ÉCRITURE des rows de la table temp :
    print("Ecriture des rows du fichier distant 'temp'")
    cpt = 0
    for row_distant in rows_temp_distant:
        try:
            app_tables.temp.add_row(
                pre_r_pour_stage = row_distant['pre_r_pour_stage'],
                # media            = row_distant['media'],
                nb_questions_qcm = row_distant['nb_questions_qcm'],
                nb_mails_sent    = row_distant['nb_mails_sent'],
                text             = row_distant['text'],
                code_stage       = row_distant['code_stage'],
                type_suivi       = row_distant['type_suivi'],
                dico_formulaire  = row_distant['dico_formulaire'],
            )
            cpt += 1
            print(f"✅ row {cpt} insérée pour code_stage '{row_distant['code_stage']}'")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion dans la table temp, code_stage: {row_distant.get('code_stage')} : {e}")
    
    print("Fin du traitement temp")
    
    print("")
    print(" ---------------------------------------------------------------------")
    print("Fin des maj des tables de base")
    
    print("")
    print(" ---------------------------------------------------------------------")
    
    
    # ---------------------------------------------------------------------------------------------------------------------------
    anvil.server.disconnect()
    
    
    # lancement du uplink maj des medias (jpg ...)
    print("Etape 2 à effectuer: maj des tables liées")
    # run_uplink_2()
    
    
    # ---------------------------------------------------------------------------------------------------------
    msg="ok"
    return msg
    
