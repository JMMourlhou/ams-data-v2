from ._anvil_designer import QCM_visu_modif_ST_MainTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..QCM_visu_modif import QCM_visu_modif
import random             # pour rechercher les qcm BNSSA randomly avec random.randrange(début, fin)
global liste
liste = []

class QCM_visu_modif_ST_Main(QCM_visu_modif_ST_MainTemplate):
    def __init__(self, qcm_descro_nb=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.qcm_row = None
        # acquisition du user
        user=anvil.users.get_user()
        self.user = user
        if user:
            #print(f"User {user['nom']} débute un Qcm")
            self.admin = user['role']
            rol = self.admin[0:1]
            if rol=="S" or rol=="T" or rol=="J":         # si stagiaire
               self.label_3.text = "Q.C.M"
        
        #initialisation du drop down des qcm créés et barêmes, n'affiche que les qcm visibles ET ds dict d'autorisations du stagiaire (table 'stagiaires inscrits')
        dict_qcm = {}  # dict contenant en clef le num qcm autorisé 
        
        #lecture du ou des dictionaires du stagiaire (il peut être inscrit à plusieurs stages)
        liste_temp_dictionaires = app_tables.stagiaires_inscrits.search(user_email=user)
        if  liste_temp_dictionaires:
            for stage in liste_temp_dictionaires:
                droits_stagiaire = {}
                if stage['droits_stagiaire_qcms']:     # je lis toutes les clefs de droits_stagiaire (qcm authorisés pour ce stage)
                    droits_stagiaire = stage['droits_stagiaire_qcms']
                    # je boucle sur ce dictionaire des qcm authorisés pour ce stage et rempli dict 
                    for clef, valeur in droits_stagiaire.items():   #clef=numqcm   valeur=("intitulé", "TRUE/False")   True si on le montre
                        #print(f"clé: {clef},valeur: {valeur[1]}")
                        if valeur[1]=="True":
                            dict_qcm[clef]= valeur  # num_qcm:intitulé 
                            #print(f"Mise en dico de : {clef}")
        # tri du dict sur l'intitulé du qcm
        dict_qcm_trie = dict(sorted(dict_qcm.items(), key=lambda item: item[1]))
                    
        # J'initialise la liste en transformant le "dict" des qcm authorisés en liste
        # boucle de "dict"
        liste_qcm_rows=[]   # liste des qcm lus
        for clef, valeur in dict_qcm_trie.items():
            #print(clef)
            # lecture sur la clef
            qcm_row = app_tables.qcm_description.get(qcm_nb=int(clef))
            if qcm_row['visible'] is True:                               # SI QCM VISIBLE
                liste_qcm_rows.append(qcm_row)                           #  INSERERE LA ROW PAS UNIQT la destination 
        if liste_qcm_rows:   
            # TRI ALPHABÉTIQUE DES QCM
            liste_qcm_rows.sort(key=lambda row: row['destination'].lower())
            self.drop_down_qcm_row.items = [(r['destination'],r) for r in liste_qcm_rows]     # initialisation de la drop down par "compréhension de liste"
        
        if qcm_descro_nb is not None:      #réinitialisation de la forme après une création ou modif
            self.qcm_nb = qcm_descro_nb # je sauve le row du qcm sur lesquel je suis en train de travailler
            # j'affiche le drop down du qcm
            self.drop_down_qcm_row.selected_value = qcm_descro_nb
            # j'envoie en drop_down_qcm_row_change
            self.drop_down_qcm_row_change()

        self.button_annuler_copy.visible = False
    
    def drop_down_qcm_row_change(self, **event_args):
        """This method is called when an item is selected"""
        
        qcm_row = self.drop_down_qcm_row.selected_value          #qcm description row
        print(f"{self.user['prenom']} {self.user['nom']} a sélectionné le QCM nb {qcm_row['qcm_nb']}, {qcm_row['destination']} ")
        if qcm_row is None:
            alert("Choisissez un QCM !")
            return
        
        self.qcm_row = qcm_row
        #print("dropD change :",qcm_row["qcm_nb"],qcm_row["qcm_source"])
        # Pour les lignes QCM déjà crée du qcm choisi
        global liste  
        #alert(qcm_row["qcm_source"])
        if qcm_row["qcm_source"] is None:                                  # si source est null : Qcm unique, non sous élement d'un QCM master
            liste = list(app_tables.qcm.search(qcm_nb=qcm_row))
        else:                                                              # si source non null : QCM master, créer à partir de qcm enfants
            dico = {}
            dico = qcm_row["qcm_source"]
            #print("------------------------------------------------------  dico: ", dico)
            liste = list(self.liste_qcm_master(dico))
        nb_questions = len(liste)
        self.label_2.text = nb_questions + 1   # Num ligne à partir du nb lignes déjà créées

        # acquisition du user et modif de son temp (nb de questions de son qcm)
        user=anvil.users.get_user()
        r = anvil.server.call("temp_user_qcm", user, nb_questions, qcm_row["qcm_nb"])
        if r is False:
            alert("user non MAJ")
            return
        # affiche le titre
        if self.admin[0:1]=="S":         # si stagiaire
               self.label_3.text = "Q.C.M " + qcm_row["destination"]
        # affiches les lignes du qcm
        self.affiche_lignes_qcm(liste)
    
    def affiche_lignes_qcm(self, l=[]):
        global liste
        self.column_panel_content.clear()
        self.column_panel_content.add_component(QCM_visu_modif(liste), full_width_row=True)
        self.button_annuler_copy.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def button_annuler2_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def liste_qcm_master(self, dico, **event_args):            # lecture des qcm enfants ds table qcm_descro /colonne dict 'qcm_source'
        global liste
        liste=[]
        for clef_NumQcm, valeur_NbQuestions in dico.items():
            liste_temp = self.liste_qcm_partie_x(int(clef_NumQcm), int(valeur_NbQuestions))   # (clef:num qcm, valeur: nb de questions à prendre randomly)
            for i in range(len(liste_temp)):
                liste.append(liste_temp[i])
        return liste

    def liste_qcm_partie_x(self, qcm_nb, nb_max, **event_args):
        liste = []
        
        #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ nb max: ", nb_max)
        #extraction du nb de questions pour le qcm Master
        qcm_row = app_tables.qcm_description.get(qcm_nb=qcm_nb)
        if qcm_row:
            liste_entierre = app_tables.qcm.search(tables.order_by("num", ascending=True),
                                                   qcm_nb=qcm_row)
            nb_total_questions = len(liste_entierre)
            print(f"nb question ds qcm_nb {qcm_nb}: {nb_total_questions}" )
        else:
            print(f"pb accès table qcm n° {qcm_nb} (enfant d'un qcm master)")
            return
            
           
        dict = {}
        if qcm_nb != 28: # tous qcm non SNV: questions triées aléatoirement 
            # SI OPTION AFFICHAGE QUESTIONS ORDRE ALEATOIRE 
            while len(dict) < nb_max:
                num_question =   random.randrange(1, nb_total_questions+1)  
                question_row = app_tables.qcm.get(qcm_nb=qcm_row,
                                                num=num_question
                                                )
                clef = num_question           # clé du dict de questions     Comme il ne peut y avoir 2 même clé, si random prend 2 fois la même question, elle écrase l'autre
                valeur = question_row
                #print("clef: ",clef)
                dict[clef] = valeur   # je mets à jour la liste dictionaire des questions
        else:
            # SINON: Lecture normale de la table entierre, triée sur le num de question
            for num_question in range(1, min(nb_max, nb_total_questions) + 1):
                question_row = app_tables.qcm.get(qcm_nb=qcm_row, num=num_question)
                clef = num_question           # clé du dict de questions     Comme il ne peut y avoir 2 même clé, si random prend 2 fois la même question, elle écrase l'autre
                valeur = question_row
                #print("clef: ",clef)
                dict[clef] = valeur   # je mets à jour la liste dictionaire des questions
        
        # Creation de la liste
        for cle, valeur in dict.items():
            liste.append(valeur)
        
        return liste

    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        user=anvil.users.get_user()
        with anvil.server.no_loading_indicator:
            result = anvil.server.call("ping")
        print(f"Module QCM user {user['nom']} {user['prenom']}, ping on server to prevent 'session expired' every 5 min, server answer:{result}")



            
        
        






