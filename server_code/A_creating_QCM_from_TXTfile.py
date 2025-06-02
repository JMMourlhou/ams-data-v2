import anvil.email
import anvil.files
from anvil.files import data_files

#anvil.users
import anvil.tables as tables
#import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# lecture d'1 fichier txt pour en extraire les données
@anvil.server.callable
def file_reading():
    # Read the contents of a file
    cpt=0                # nb de questions
    question_txt = ""    # la question incluant l'intitilé et les options
    rep =""              # dernier caractère d'une option 1 si vrai, 0 si faux
    nb_de_choix = 0      # nb d'options ex: A, B, C  = 3 options
    f = open(data_files['qcm_2_14_mars_2025.txt'])              # <-----------------------------------------------------  à modifier      fichier text entré en assets
    x = True
    n="" # 1er caractère à tester pour savoir si la ligne est une question
    while x:
        ligne = f.readline()  # lecture  1 ligne
        
        if not ligne:                                        # FIN DE FICHIER TEXT           #rep = rep + dernier_caract
            resume(cpt, nb_de_choix, question_txt, rep)
            print('Fin du fichier')
            break
            
        n = ligne[0:1]   # Je prends le 1er caract de ligne
        try:
            num = int(n) # cette ligne est le début d'une question car contient un nombre
            new_question = True
        except ValueError:
            new_question = False
       
        if new_question: 
            # cette ligne est la 1ere ligne de la question (le thème de cette question BNSSA)
            resume(cpt, nb_de_choix, question_txt, rep)  
            rep = ""
            nb_de_choix = 0
            dico = {}
            cpt += 1     # incrément du num de questions ds ce qcm
            cpt_lignes_ds_question = 0
            question_txt = ""  # je remets à "" ma question
            
        if not new_question:    
            # cette ligne n'est pas la 1ere ligne de la question mais une des options
            cpt_lignes_ds_question += 1
            dernier_caract = ligne[len(ligne)-2:len(ligne)-1]    # je prends la réponse au dernier caract (0 ou 1) je commence 2 caract avt la fin car le dernier est un retour ligne
            if not cpt_lignes_ds_question == 1:   # je ne suis plus ds l'entete de la question, avant les options
                nb_de_choix += 1
                ligne = ligne[0:len(ligne)-2]+ "\n"
                # creation du code de la réponse: sur 2,3,ou 4 caract 
                rep = rep + dernier_caract
            if cpt_lignes_ds_question == 1:
                question_txt = question_txt + ligne + "\n"
            else:
                txt = ligne[0:1] + "  " + ligne[2:len(ligne)] + "\n"
                question_txt = question_txt + txt
    f.close()

def resume(cpt, nb_de_choix, question_txt, rep):       
     # SAUVER LA QUESTION précédente, SON NUM et le nb de choix et les réponses 
    if cpt != 0:
        #rep = rep[1:len(rep)]
        print(f"question # {cpt}, nb de choix: {nb_de_choix}, question:{question_txt}, réponse codée: {rep}")   
        print()
    
    # Préparation de l'intertion ds table QCM
    param = "BNSSA 2 'Diplômes, compétences et obligations'"                     # <-----------------------------------------------------  à modifier
    bareme = "1"
    qcm_nb = 21
    # Lecture du fichier qcm descro pour obtenir le row
    qcm_descro_row=app_tables.qcm_description.get(qcm_nb=qcm_nb)
    if qcm_descro_row:
        print("ok")
    
        "création de la ligne qcm ds table qcm"
        new_row=app_tables.qcm.add_row(
                                   num= cpt,
                                   question = question_txt,
                                   correction = None,
                                   rep_multi = rep,
                                   bareme = bareme,
                                   photo = None,
                                   qcm_nb = qcm_descro_row,
                                   param = param
                                    )
    else:
        print("qcm_descro non trouvé")


        
            
            
        
