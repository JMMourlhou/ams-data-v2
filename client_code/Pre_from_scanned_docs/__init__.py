from ._anvil_designer import Pre_from_scanned_docsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .student_row import student_row

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
        dico_pre_requis = stage_row["code"]['pre_requis']
        self.drop_down_pr.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if dico_pre_requis.get(r["code_pre_requis"])]
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
        self.pr_row = self.drop_down_pr.selected_value
        #self.button_ok.visible = True
        self.file_loader_docs_pr.visible = True
        self.drop_down_pr.background = "blue"

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
        self.button_ok.visible = True
