from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Box_types_fi import Box_types_fi
from ...Box_stages import Box_stages
import time
from ... import French_zone # calcul tps traitement


class RowTemplate1(RowTemplate1Template):
    def __init__(self, **properties):
        self.c = get_open_form()
        #print("form mère en col panel : ", self.c) 
        
        self.content_panel.clear() # Panel qui recevra la forme du choix de type de fi
        
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.repeating_panel_1.visible = False  #qcm non visibles tant que pas de click sur bt Qcm
        self.user_initial_color()
        try: # *********************************          Liste à partir table users
            self.email_pour_del = self.item 
            if self.item['prenom'] is not None:    # si prénom None, erreur
                self.button_1.text = self.item['nom']+" "+self.item['prenom']
         
                self.button_role.text = self.item['role']
                  
            else:
                self.button_1.text = self.item['nom']
                
            tel = self.item['tel']
            self.button_4.text = self.item['email']
            self.button_qcm.tag = self.item['email']
            self.button_histo.tag = self.item['email']
            self.drop_down_code_stage.tag = self.item['email']
            user_row = app_tables.users.get(q.fetch_only("nom","prenom","tel","email"),
                                            email=self.item['email']) # pour pré-requis  
        except: # ***********************************  Liste à partir table Stagiaires inscrits
            mel = self.item['user_email']['email']
            self.email_pour_del = self.item['user_email']
            user_row = app_tables.users.get(q.fetch_only("nom","prenom","tel","email"),
                                            email=mel)
            #stagiaire_row = user_row # pour les pré-requi
            self.button_1.text = user_row['nom']+" "+user_row['prenom']
            tel = user_row['tel']
            self.button_4.text = user_row['email']
            self.button_histo.tag = user_row['email']
            self.drop_down_code_stage.tag = user_row
            self.button_role.text = self.item['user_email']['role']
            
        if tel is not None:    
            a = tel[0:2]   # mise en forme du tel
            b = tel[2:4]
            c = tel[4:6]
            d = tel[6:8]
            e = tel[8:10]
            self.button_3.text = a+"-"+b+"-"+c+"-"+d+"-"+e    
            
        # Si ADMINISTRATEUR ou BUREAUX je visualise le BT del (effacement d'un stagiaire, formateur, tuteur)
        user = anvil.users.get_user()
        if user["role"] == "A" or user["role"] == "B":
            self.button_del.visible = True
        """
        # Drop down stages inscrits du stagiaire pour les pré-requis du stage sélectionnés
        start = French_zone.french_zone_time()  # pour calcul du tps de traitement
        
        liste0 = app_tables.stagiaires_inscrits.search( q.fetch_only("stage_txt"),
                                                           user_email=user_row)
        liste_drop_d = []
        for row in liste0:
            liste_drop_d.append((row["stage_txt"], row))
        self.drop_down_code_stage.items = liste_drop_d
        
        end = French_zone.french_zone_time()
        print("Temps de traitement init drop dwn: ", end-start)
        """
    # button_1 : nom du stagiaire
    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""

        # self.c.label_num_stage.text   est en forme mère recherche_stagiaire_v2
        print("Mode inscription si stage pas vide: ",self.c.label_origine.text, self.c.label_num_stage.text)
        if self.c.label_origine.text == "<AMS_Data.Main.Main object>" or self.c.label_num_stage.text == "":    # vient du menu / recherche, pas d'inscription // 
            try:
                mel = self.item['email']   
            except:
                mel = self.item['user_email']['email']

            from ...Saisie_info_apres_visu import Saisie_info_apres_visu
            open_form('Saisie_info_apres_visu', mel, num_stage=0, intitule="")
        else:   # inscription d'un stagiaire ou d'un tuteur
            mel = self.item['email']
            stagiaire_row = app_tables.users.get(email=mel)
            stage = self.c.label_num_stage.text
            print(f"stage en inscription: <{stage}>")
            
            self.content_panel.visible = True
            if int(stage) != 1003:   # tous stages sauf tuteurs
                self.content_panel.add_component(Box_types_fi(stagiaire_row, stage), full_width_row=False)
            else:  # Ajout d'un Tuteur   
                self.content_panel.add_component(Box_stages(stagiaire_row, stage), full_width_row=False)
            self.content_panel.scroll_into_view()
 
    
    def button_role_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_1_click()    
        
    def button_3_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_1_click()

    def button_4_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_1_click()

    def button_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.repeating_panel_1.visible is False:
            self.repeating_panel_1.visible = True
            self.button_qcm.foreground = "red"
            self.button_1.foreground = "red"
            try:  # si recherche sur la table users
                stagiaire = app_tables.users.get(email=self.item['email'])
                qcm_results = app_tables.qcm_result.search( 
                                                            tables.order_by("time", ascending=False),
                                                            user_qcm = stagiaire
                                                            )
                if self.item['role'] == "A" or self.item['role'] == "B" or self.item['role'] == "J":          # Admin en rouge
                    self.button_1.foreground = "red"
                if self.item['role'] == "F":
                    self.button_1.foreground = "blue"  # Formateur en bleu
                if self.item['role'] == "T":
                    self.button_1.foreground = "green"  # Formateur en bleu    
            except: # si recherche sur la table stagiaire_inscrit
                stagiaire = app_tables.users.get(email=self.item['user_email']['email'])
                qcm_results = app_tables.qcm_result.search(
                                                            tables.order_by("time", ascending=False),
                                                            user_qcm = stagiaire
                                                            )
                if stagiaire['role'] == "A":          # Admin en rouge
                    self.button_1.foreground = "red"
                if stagiaire['role'] == "F":
                    self.button_1.foreground = "blue"  # Formateur en bleu
            if len(qcm_results)>0:      # qcm trouvés pour ce user
                    self.repeating_panel_1.items = qcm_results
        else:
            self.repeating_panel_1.visible = False
            self.button_qcm.foreground = "yellow"
            self.user_initial_color()        

    def button_histo_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.repeating_panel_2.visible is False:
            self.repeating_panel_2.visible = True
            self.button_histo.foreground = "red"
            self.button_1.foreground = "red"
            
            try:  # si recherche sur la table users
                stagiaire = app_tables.users.get(email=self.item['email'])
                if self.item['role'] == "A":          # Admin en rouge
                    self.button_1.foreground = "red"
                if self.item['role'] == "F":
                    self.button_1.foreground = "blue"  # Formateur en bleu
            except:
                stagiaire = app_tables.users.get(email=self.item['user_email']['email'])
                if stagiaire['role'] == "A":          # Admin en rouge
                    self.button_1.foreground = "red"
                if stagiaire['role'] == "F":
                    self.button_1.foreground = "blue"  # Formateur en bleu
            self.repeating_panel_2.items = app_tables.stagiaires_inscrits.search(user_email = stagiaire)
        else:
            self.repeating_panel_2.visible = False
            self.button_histo.foreground = "yellow"
            self.user_initial_color()
            

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        self.repeating_panel_3.visible = True
        self.drop_down_code_stage.foreground = "red"
        self.button_1.foreground = "red"
        
        row_stagiaire_inscrit = self.drop_down_code_stage.selected_value   # Stage sélectionné du user ds drop_down (row table stagiaire inscrit)
        if row_stagiaire_inscrit is not None:
            # lecture fichier père stages
            row_stage = app_tables.stages.get(numero=row_stagiaire_inscrit['stage']['numero'])
            #print(row_stage['numero'])
            # lecture des pré requis pour ce stage et pour ce stagiaire
            stagiaire_email = self.drop_down_code_stage.tag
            try:
                stagiaire_row = app_tables.users.get(email=stagiaire_email['email'])
            except:
                stagiaire_row = app_tables.users.get(email=stagiaire_email)
                
            liste_pr = app_tables.pre_requis_stagiaire.search(stagiaire_email=stagiaire_row,
                                                            stage_num=row_stage
                                                            )
            print(len(liste_pr))
            self.repeating_panel_3.items = liste_pr
        else:
            self.repeating_panel_3.visible = False
            self.drop_down_code_stage.foreground = "yellow"
            self.user_initial_color()

    def button_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        liste_email = []
        liste_email.append((self.button_histo.tag,self.item['prenom'],""))   # mail et prénom, id pas besoin
        open_form('Mail_subject_attach_txt',liste_email,"stagiaire_1")

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Effacement du stagiaire/formateur si pas ds un stage et si je suis l'administrateur
        user = anvil.users.get_user()
        if user["role"] == "A" or user["role"]=="B":   # seul,l'administrateur et bureaux peuvent effacer definitivement un stagiaire ou formateur ou tuteur
            # Cette personne est-elle inscrite ds un ou plusieurs stages ?
            list = app_tables.stagiaires_inscrits.search(user_email=self.email_pour_del)
            detail =""
            for stage in list:
                detail=detail+str(stage['numero'])+"  "
                
            nb_stages = len(list)
            if nb_stages != 0:
                txt="stage"
                if nb_stages > 1:
                    txt = "stages"
                alert(f"Effacement impossible:\nCette personne est inscrite dans {nb_stages} {txt}\n\n Détail:\n{txt} N°{detail}")
                self.button_histo_click()   # visu de l'histo du stagiaire
                return
            # Effact de la personne si confirmation
            r=alert("Voulez-vous vraiment enlever définitivement cette personne ? ",dismissible=False ,buttons=[("oui",True),("non",False)])
            if r :   # oui
                # lecture row users
                row = app_tables.users.get(email=self.email_pour_del['email'])
                if row:
                    txt_msg = anvil.server.call("del_personne",row)
                alert(txt_msg)
            open_form("Recherche_stagiaire_v2")

    def user_initial_color(self):
        try:
            role = self.item['role']
        except:   
            role = self.item['user_email']['role']
            
        if role == "A" or role == "B" or role == "J":          # Admin en rouge
            self.button_1.foreground = "red"   # Bureaux en rouge
        if role == "F":
            self.button_1.foreground = "blue"  # Formateur en bleu
        if role == "T":
            self.button_1.foreground = "green"  # Tuteur en vert
        if role == "S":
            self.button_1.foreground = "yellow"  # Stagiaire en jaune

    def button_pr_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_3.visible = True
        self.drop_down_code_stage.foreground = "red"
        self.button_1.foreground = "red"

        # Acquisition des stages où le stagiaire est inscrit
        try:  # *********************************          Liste à partir table users
            liste0 = app_tables.stagiaires_inscrits.search( q.fetch_only("stage_txt"),
                                                            user_email=self.item)
        except:  # ***********************************  Liste à partir table Stagiaires inscrits
            liste0 = app_tables.stagiaires_inscrits.search( q.fetch_only("stage_txt"),
                                                            user_email=self.item['user_email'])
        if liste0 is None:
            return

        # pour chaque stage, je lis les pré requis en table pré requis stagiaires
        # Création du dict des pr du stagiaire
        self.dico_pre_requis = {}
        for stage in liste0:
            liste_pr = app_tables.pre_requis_stagiaire.search(stagiaire_email=stage['user_email'],
                                                              numero=stage['numero']
                                                             )
            # création du dico des pré-requis 
            # print(liste_pr[0])

            for pr in liste_pr:
                valeur = None
                clef = pr['requis_txt']
                valeur = (pr['stage_num'], pr['item_requis'], pr['code_txt'], pr['stagiaire_email'], pr['doc1'])
                # Si la clé n'existe pas encore, ou si la valeur actuelle est None et la nouvelle non None
                if clef not in self.dico_pre_requis  or  (self.dico_pre_requis[clef][1] is None and pr['doc1'] is not None):
                    self.dico_pre_requis[clef] = valeur
        
        # Fin de boucle le dico contient le résumé de tous les pr du stagiare et True si présent        
        """
        for clef in self.dico_pre_requis:
            print (clef,self.dico_pre_requis[clef])
        """
        # Transformation en liste
        # -----------------------------------------------------------
        # Transformation en liste pour affichage dans le RepeatingPanel
        liste_affichage = []
        
        for clef, (numero, requis_row, type_stage_txt ,email, doc1) in self.dico_pre_requis.items():
            liste_affichage.append({
                "requis_txt": clef,
                "item_requis": requis_row,
                "type_stage_txt": type_stage_txt,
                "stagiaire_email": email,
                "stage_num": numero,
                "doc1": doc1
            })
        
        # Affectation au RepeatingPanel pour affichage
        self.repeating_panel_3.items = liste_affichage
        








        
        
        