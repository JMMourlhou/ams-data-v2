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
        self.column_panel_menu.visible = True

    def button_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.f.repeating_panel_qcm.visible is False:
            self.repeating_panel_qcm.visible = True
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
        pass

    def button_pr_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
