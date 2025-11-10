from ._anvil_designer import Pre_from_scanned_docsTemplate
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class Pre_from_scanned_docs(Pre_from_scanned_docsTemplate):
    def __init__(self, stage_row, **properties):
        # Set Form properties and Data Bindings.

        # Any code you write here will run before the form opens.
        self.init_components(**properties)
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
        self.nb_stagiaires = len(self.liste)
        self.repeating_panel_stagiaire_inscrits.items = self.liste
        
    def drop_down_pr_change(self, **event_args):
        """This method is called when an item is selected"""
        self.pr_row = self.drop_down_pr.selected_value
        #self.button_ok.visible = True
        self.file_loader_docs_pr.visible = True
        
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
        r=alert(f"Les documents scannés sont-ils bien pour {self.nb_stagiaires}stagiaires ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if not r :   # non
            return
        r=alert(f"Avez-vous décochés les stagiaires qui n'ont pas leurs documents dans le fichier pdf des {self.drop_down_pr.selected_value['requis']} ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if not r :   # non
            return   
        #txt_msg = anvil.server.call("", self.file, self.stage_row, self.pr_row)
        txt_msg = "ok"
        alert(txt_msg)
        open_form(self.f)

    def file_loader_docs_pr_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.file = file
        self.button_ok.visible = True
        