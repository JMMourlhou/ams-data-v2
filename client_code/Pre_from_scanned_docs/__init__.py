from ._anvil_designer import Pre_from_scanned_docsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .student_row import student_row
from .pr_selected_list import pr_selected_list

global dico_pre_requis_selected   # le dictionaire des PR sélectionnés par drop down pour travailler sur le PDF 
dico_pre_requis_selected = {}

global dico_pre_requis_initial   # le dictionaire des PRpour ce stage
dico_pre_requis_initial = {}

class Pre_from_scanned_docs(Pre_from_scanned_docsTemplate):
    def __init__(self, stage_row, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        global dico_pre_requis_initial   # le dictionaire des PRpour ce stage
        # Any code you write here will run before the form opens.
        self.file = None
        self.f = get_open_form()
        self.stage_row = stage_row
        self.text_box_stage.text = f"{self.stage_row['code_txt']} du {str(self.stage_row['date_debut'])} {str(self.stage_row['numero'])}"

        # INITIALISATION Drop down pré-requis
        dico_pre_requis_initial = stage_row["code"]['pre_requis']
        for key in dico_pre_requis_initial:
            print(f"dico initial en init: {key}")
        self.drop_down_pr.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if dico_pre_requis_initial.get(r["code_pre_requis"])]
        if len(self.drop_down_pr.items)==0:  # si le dictionaire n'existe pas encore (pas de pré requis encore introduit pour ce type de stage)
            alert("Pas de PR pour ce stage en table codes_stages !")
            return

        # initialisation liste des stagiaires du stage
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
                        
    def handle_change_check_box(self, sender, **event_args):
        #alert(sender.check_box_state)
        alert(sender.row_stagiaire_inscrit['name'])
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
        else:
            clef = row["code_pre_requis"]  #extraction de la clef à ajouter à partir de la row sélectionnée de la dropbox
            valeur = (row["requis"], row["order"])
            dico_pre_requis_selected[clef] = valeur
        
            # Ajout du PR ds les la liste des PR sélectionnés PR sélectionnés
            list_keys = dico_pre_requis_selected.keys()
            list_keys = sorted(list_keys)  # création de la liste triée des clefs du dictionaires prérequis
            print(f"liste des clefs/dico_pre_requis_selected: {list_keys}")
            
            #self.repeating_panel_1.items = list(list_keys)   # liste des clefs (pré requis)
            for pr_key in list_keys:
                new_row = student_row(pr_selected_list)
                new_row.pr_code_to_be_deleted = pr_key  # row_stagiaire_inscrit: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
                new_row.set_event_handler('x-del', self.handle_del_pr)  # si event: bouton del est cliqué
                self.content_panel_pr.add_component(new_row)

            self.button_valid_pr_list.visible = True
            
            self.pr_row = self.drop_down_pr.selected_value
            self.file_loader_docs_pr.visible = True
            self.drop_down_pr.selected_value = None
            
            # j'enlève la clef sélectionnée du dico des pr initial pour ré-initialiser la dropdown
            print(f"clef à enlever: {clef}")
            print("dico_pre_requis_initial:")
            for key in dico_pre_requis_initial:
                print(f"dico initial en modif du drop down: {key}")
            
            del dico_pre_requis_initial[clef]
            #réinitialisation dropdown pré requis sans le pré requis sélectionné
            #self.drop_down_pr.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if not dico_pre_requis.get(r["code_pre_requis"])]
            self.drop_down_pr.items = [(r["requis"], r) for r in  app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if dico_pre_requis_initial.get(r["code_pre_requis"])]
            
    def handle_del_pr(self, sender, **event_args):
        pass
        # ajouter le pr_code du dico dico_pre_requis_initial 

        # enlever le pr_code du dico 
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)

    def button_ok_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.file is None:
            alert("Sélectionner le fichier pdf !")
            return
        if self.drop_down_pr.selected_value is None:
            alert("Sélectionner le pré-requis !")
            return
        r=alert(f"Les documents scannés sont-ils bien pour {self.text_box_nb_stagiaires_marked.text} stagiaires ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if not r :   # non
            return
        r=alert(f"Avez-vous décochés les stagiaires qui n'ont pas leurs documents dans le fichier pdf des {self.drop_down_pr.selected_value['requis']} ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if not r :   # non
            return   
        # Création du dico
        
        # ajout ds le dico par boucle sur les composents 'student_row', avec test si 
        dico = {}
        cpt = 0
        for ligne in self.content_panel.get_components():
            for cp in ligne.get_components():
                for component in cp.get_components():
                    if isinstance(component, anvil.CheckBox):
                        alert("CheckBox ")
                        
                        if component.checked is True:
                            cpt += 1
                            cle = cpt
                            valeur = (ligne.row_stagiaire_inscrit['stage'], ligne.row_stagiaire_inscrit['user_email'])
                            dico[cle] = valeur
                            
        alert(len(dico[cle]))
        #txt_msg = anvil.server.call("", self.file, self.stage_row, self.pr_row)
        txt_msg = "ok"
        alert(txt_msg)
        open_form(self.f)

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