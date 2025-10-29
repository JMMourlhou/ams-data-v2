from ._anvil_designer import RowTemplate9Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate9(RowTemplate9Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()
        if self.item['prenom'] is not None:    # si prénom None, erreur
            self.button_1.text = self.item['nom']+" "+self.item['prenom']
            self.button_role.text = self.item['role']
        else:
            self.button_1.text = self.item['nom']

        self.button_3.text = self.item['email']
        self.button_4.text = self.item['tel']

    def button_role_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Affichage des infos sur lequel je travaille 
        self.f.button_role.text = self.button_role.text
        self.f.button_1.text = self.button_1.text
        self.f.button_3.text = self.button_3.text
        self.f.button_4.text = self.button_4.text
        # Sov le user_email
        self.f.label_user_email.text = self.item['email']
        self.f.column_panel_stagiaire.visible = True
        self.f.column_panel_menu.visible = True


    def button_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        if self.f.repeating_panel_qcm.visible is False:
            self.f.repeating_panel_qcm.visible = True
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
                self.f.repeating_panel_qcm.items = qcm_results
                
        else:
            self.f.repeating_panel_qcm.visible = False
            self.button_qcm.foreground = "yellow"
            #self.user_initial_color()        

    def button_histo_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.f.repeating_panel_histo.visible is False:
            self.f.repeating_panel_histo.visible = True
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
            self.f.repeating_panel_histo.items = app_tables.stagiaires_inscrits.search(user_email = stagiaire)
        else:
            self.f.repeating_panel_histo.visible = False
            self.button_histo.foreground = "yellow"
            #self.user_initial_color()

    def button_pr_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Acquisition des stages où le stagiaire est inscrit
        try:  # *********************************          Liste à partir table users
            liste0 = app_tables.stagiaires_inscrits.search( q.fetch_only("stage_txt"),
                                                            user_email=self.item)
        except:  # ***********************************  Liste à partir table Stagiaires inscrits
            liste0 = app_tables.stagiaires_inscrits.search( q.fetch_only("stage_txt"),
                                                            user_email=self.item['user_email'])
        if liste0 is None:
            return
        if self.repeating_panel_pr.visible is False:
            self.repeating_panel_pr.visible = True
            self.button_pr.foreground = "red"
            self.button_1.foreground = "red"

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
            if liste_affichage != []:
                self.repeating_panel_pr.items = liste_affichage
            else:
                self.repeating_panel_pr.visible = False
                self.button_pr.foreground = "yellow"
                #self.user_initial_color()

    def button_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
