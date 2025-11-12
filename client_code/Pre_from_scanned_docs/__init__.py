from ._anvil_designer import Pre_from_scanned_docsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .student_row import student_row
from .pre_requis_selected import pre_requis_selected

global dico_pre_requis_selected   # le dictionaire des PR sélectionnés par drop down pour travailler sur le PDF 
dico_pre_requis_selected = {}

global dico_pre_requis_initial   # le dictionaire des PRpour ce stage
dico_pre_requis_initial = {}

class Pre_from_scanned_docs(Pre_from_scanned_docsTemplate):
    def __init__(self, stage_row, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        
        # Any code you write here will run before the form opens.
        self.file = None
        self.f = get_open_form()
        self.stage_row = stage_row
        self.text_box_stage.text = f"{self.stage_row['code_txt']} du {str(self.stage_row['date_debut'])} {str(self.stage_row['numero'])}"

        # INITIALISATION Drop down pré-requis
        global dico_pre_requis_initial   # le dictionaire des PRpour ce stage
        dico_pre_requis_initial = {}
        global dico_pre_requis_selected   # le dictionaire des PR sélectionnés par drop down pour travailler sur le PDF 
        dico_pre_requis_selected = {}
        
        dico_pre_requis_initial = stage_row["code"]['pre_requis']
        for key in dico_pre_requis_initial:
            print(f"dico initial en init: {key}")
        self.drop_down_pr.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if dico_pre_requis_initial.get(r["code_pre_requis"])]
        if len(self.drop_down_pr.items)==0:  # si le dictionaire n'existe pas encore (pas de pré requis encore introduit pour ce type de stage)
            alert("Pas de PR pour ce stage en table codes_stages !")
            return

        # initialisation liste des stagiaires du stage en créant 1 form student_row dans content_panel
        self.liste = list(app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True),
            stage=self.stage_row
        ))    
        self.text_box_nb_stagiaires_marked.text = len(self.liste)
        cpt = 1
        for row_stagiaire_inscrit in self.liste: 
            new_row = student_row(cpt, row_stagiaire_inscrit)
            new_row.row_stagiaire_inscrit = row_stagiaire_inscrit  # row_stagiaire_inscrit: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
            new_row.set_event_handler('x-change', self.handle_change_check_box)
            self.content_panel.add_component(new_row)
            cpt += 1

    # Event raised: Changement du check box du stagiaire
    def handle_change_check_box(self, sender, **event_args):
        #alert(sender.row_stagiaire_inscrit['name'])
        nb_de_stagiaires = int(self.text_box_nb_stagiaires_marked.text)
        if sender.check_box_state is False:
            nb_de_stagiaires -= 1
        else:
            nb_de_stagiaires += 1
        self.text_box_nb_stagiaires_marked.text = nb_de_stagiaires
        
    def drop_down_pr_change(self, **event_args):
        """This method is called when an item is selected"""
        global dico_pre_requis_initial
        global dico_pre_requis_selected
        row = self.drop_down_pr.selected_value       # row du pre_requis 
        if row is None:
            alert("Vous devez sélectionner un pré-requis !")
            self.drop_down_pr.focus()
            return

        # Ajout du PR ds le dico des clés des PR sélectionnés
        clef = row["code_pre_requis"]  #extraction de la clef à ajouter à partir de la row sélectionnée de la dropbox
        valeur = (row)
        dico_pre_requis_selected[clef] = valeur
        print(f"Nb de clés sélectionnées: {len(dico_pre_requis_selected)}")
        
        # Affichage Du pr SELECTIONNE par ajout de la form pre_requis_selected, 
        new_row = pre_requis_selected(row)
        new_row.pr_code_to_be_deleted = row  # row_stagiaire_inscrit: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        new_row.set_event_handler('x-del', self.handle_del_pr)  # si event: bouton del est cliqué
        self.content_panel_pr.add_component(new_row)
        self.content_panel_pr.visible = True

        # j'enlève la clef sélectionnée du dico des pr initial pour ré-initialiser la dropdown
        del dico_pre_requis_initial[clef]
        self.drop_down_pr.items = [(r["requis"], r) for r in  app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if dico_pre_requis_initial.get(r["code_pre_requis"])]
        print(f"Nb de clés restantes à sélectionner: {len(dico_pre_requis_initial)}")
        
        self.button_valid_pr_list.visible = True
        self.file_loader_docs_pr.visible = True
        self.drop_down_pr.selected_value = None
            
    def handle_del_pr(self, sender, **event_args):
        global dico_pre_requis_initial
        global dico_pre_requis_selected
        pr = sender.pr_row_to_be_deleted
        #alert(pr['requis'])
        # ajouter le pr_code du dico dico_pre_requis_initial 
        clef = pr["code_pre_requis"]
        valeur = (pr['requis'], pr["order"])
        dico_pre_requis_initial[clef] = valeur
        self.drop_down_pr.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if dico_pre_requis_initial.get(r["code_pre_requis"])]
        # enlever le pr_code du dico_pre_requis_selected
        del dico_pre_requis_selected[clef]
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)

    def button_ok_click(self, **event_args):
        """This method is called when the button is clicked"""
        global dico_pre_requis_selected
        if self.file is None:
            alert("Sélectionner le fichier pdf !")
            return
        r=alert(f"Si un Stagiaire n'a pas donné son document, désélectionnez-le !\nTraitement pour {self.text_box_nb_stagiaires_marked.text} stagiaire(s) ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if not r :   # non
            return    
            
        nb_pages = int(self.text_box_nb_stagiaires_marked.text) * len(dico_pre_requis_selected)
        r=alert(f"Le nb de pages du PDF doit être de: {nb_pages}, \n\n ET... \n\n classé par ordre alphabétique !",dismissible=False,buttons=[("oui",True),("non",False)])
        if not r :   # non
            return
            
        # Création du dico
        # ajout ds le dico par boucle sur les composents 'student_row', avec test si checked = True
        dico_st = {}
        cpt = 0
        for ligne in self.content_panel.get_components():
            for cp in ligne.get_components():
                for component in cp.get_components():
                    if isinstance(component, anvil.CheckBox):
                        if component.checked is True:
                            cpt += 1
                            cle = cpt
                            row_stagiaire_inscrit = component.tag
                            row_stage = row_stagiaire_inscrit['stage']
                            row_stagiaire = row_stagiaire_inscrit['user_email']
                            valeur = (row_stage, row_stagiaire)
                            dico_st[cle] = valeur
                        print(f"nb students checkTrue : {len(dico_st)}")
                            
                           
        
        #tri du dictionaire pre requis sélectionnés sur les clefs (l'utilisateur peut les avoir rentré ds n'importe quel sens)
        liste_des_clefs = dico_pre_requis_selected.keys()   #création de la liste des clefs du dictionaires prérequis
        liste_triée_des_clefs = sorted(liste_des_clefs)  # création de la liste triée des clefs du dictionaires prérequis
        
        dico_pre_requis_trié = {}
        for key in liste_triée_des_clefs:
            dico_pre_requis_trié[key] = dico_pre_requis_selected[key]
        print(f"dico des pr sélectionnés triés: {dico_pre_requis_trié}")
        print(f"nb de pr sélectionnés: {len(liste_triée_des_clefs)} ")
        print()
        # Unification des 2 dicos: PR & stagiaires en un seul dico result
        # boucle sur le dico des stagiaires
        result = {}
        page = 1
        student_cpt = 1
        for clef_student, valeur_student in dico_st.items() :                 # boucle sur le dico des stagiaires
            for clef_pr, valeur_pr in dico_pre_requis_trié.items():      # boucle sur le dico des pré-requis
                print(f"boucle sur clé pr: {clef_pr}")
                #key = str(page)
                value = ( 
                        valeur_student[0],   # stage row
                        valeur_student[1],   # student row
                        valeur_pr        # pr_row
                        )
                print(f"page {page}")
                result[page]=value
                page += 1
            student_cpt += 1                
        
            
        # vérification : nb de pages du pdf = nb de clés du dico result
        for clef,val in result.items():
            print(f"{clef}")
            print(f"stage row: {val[0]}")
            print(f"student row: {val[1]}")
            print(f"pr_row: {val[2]}")
            print()
        #print(len(result))

        #txt_msg = anvil.server.call("", self.file, self.stage_row, self.pr_row)
        txt_msg = "ok"
        alert(txt_msg)
        self.button_annuler_click()
        
    def file_loader_docs_pr_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.file = file
        self.column_panel_pr_requis.visible = True
        self.file_loader_docs_pr.background = "green"

    def button_valid_pr_list_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.content_panel.visible = True
        self.button_ok.visible = True
        self.label_stagiaires.visible = True
        self.drop_down_pr.background = "green"
        self.button_valid_pr_list.background = "green"