from ._anvil_designer import RowTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Visu_stages
from anvil import open_form
from ...Pre_R_pour_stagiaire_admin import Pre_R_pour_stagiaire_admin
from ...Recherche_stagiaire import Recherche_stagiaire
from ... import Mail_valideur  # pour button_export_xls_click

#import anvil.js    # pour screen size
from anvil.js import window # to gain access to the window object, validation du mail saisi
global screen_size
screen_size = window.innerWidth

class RowTemplate3(RowTemplate3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.mail = "jmmourlhou@gmail.com"
        # Any code you write here will run before the form opens.
        app_user = anvil.users.get_user()
        if app_user['role'] == "J":
            self.button_inscription.visible = False
            self.button_del_stage.visible = False
        self.button_qcm.tag.stage = self.item['numero']  #numero de stage en tag du bouton self.button_qcm
        
        # Affichage en fonction largeur écran
        if screen_size < 800:
            self.text_box_2.font_size = 12
            self.text_box_1.visible = False   # numéro du stage non visible
            self.button_del_stage.visible = False  # BT annulation du stage non visible
            self.button_sending.text = ""
            self.button_trombi.text = ""
            self.button_export_xls.text = ""
            if self.item['date_debut'] is not None:
                self.text_box_3.text = self.item['date_debut'].strftime("%m/%Y")   # format date française avec fonction Python strftime
        else:
            self.text_box_1.visible = True
            self.button_inscription.text = "Inscription"
            self.button_pre_requis.text = "Pré-requis"
            if self.item['date_debut'] is not None:
                self.text_box_3.text = self.item['date_debut'].strftime("%d/%m/%Y")   # format date française avec fonction Python strftime
            self.button_qcm.text = "Résultats des QCM"
        
        self.text_box_1.text = self.item['numero']
        stage = self.item['code']['code']
        stage = stage.strip()
        if len(self.item['commentaires'])>2:
            self.text_box_2.text = self.item['code']['code']+" "+self.item['commentaires'][0:5] # ajout des 5 1eres lettres du commentaire (pour quel stage)
        else:
            # pour aligner correctement les boutons
            lg = len(self.text_box_2.text)
            espace = 10-lg
            espace_caractère = " "
            while espace+len(espace_caractère)<10:
                espace_caractère = espace_caractère + " "
            self.text_box_2.text = self.item['code']['code'] + espace_caractère
            
        # Affichage du bouton d'envoi des attestations s'ils sont sauvés
        # (si la colonne 'diplomes' n'est pas None)  
        if self.item['diplomes'] is not None:
            self.button_attestations.visible = True

    # récupération par l'event:
    def text_box_3_click(self, **event_args):   # Click sur date
        """This method is called when the button is clicked"""
        self.text_box_1_click()
        
    def text_box_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        num_stage = int(self.text_box_1.text)
        id = self.item.get_id()
        open_form('Stage_visu_modif', num_stage, id)   
            

            
    def text_box_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.text_box_1_click()

    def button_inscription_click(self, **event_args):
        """This method is called when the button is clicked"""
        num_stage = self.text_box_1.text
        if num_stage != "1003":
            n = Notification("Recherchez le Stagiaire ou Formateur à inscrire", timeout=1)   # par défaut 2 secondes
        else:
            n = Notification("Recherchez le Tuteur à inscrire", timeout=1)   # par défaut 2 secondes
        n.show()
        open_form('Recherche_stagiaire',num_stage)

    def button_pr_requis_click(self, **event_args):
        """This method is called when the button is clicked"""
        num_stage = int(self.text_box_1.text)
        open_form('Pre_R_pour_stagiaire_admin',num_stage)

    def button_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        #lecture du stage du stage à partir du tag du bt self.button_qcm
        num_stage_int = self.button_qcm.tag.stage
        # lecture du stage
        stage_row = app_tables.stages.get(numero=num_stage_int)
        if stage_row:
            #print("stage: ", stage_row['numero'])
            from ...QCM_Results import QCM_Results
            open_form('QCM_Results', stage_row)

    def button_del_stage_click(self, **event_args):     # Effact du stage si pas de stagiaire
        """This method is called when the button is clicked"""
        # Stagiaires ds le stage ?
        liste_test = app_tables.stagiaires_inscrits.search(numero=self.item['numero'])
        if len(liste_test) == 0:
            # acquistion durow id pour éviter les erreurs 
            row_id = self.item.get_id()
            result = anvil.server.call('del_stage',row_id, self.item['numero'] )
            if result is True:
                alert("Stage annulé !")
                open_form('Visu_stages')
            else:
                alert("Stage non trouvé, annulation impossible")
        else:
            msg = f"{str(self.item['numero'])} {self.item['code']['code']}"
            alert(f"Ce stage {msg} contient {len(liste_test)} stagiaires, vous ne pouvez pas l'annuler !")    

    def button_sending_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Stagiaires ds le stage ?
        liste_stagiaires = app_tables.stagiaires_inscrits.search(numero=self.item['numero'])
        if liste_stagiaires:
            liste_email = []
            for stagiaire in liste_stagiaires:
                liste_email.append((stagiaire["user_email"]["email"], stagiaire["prenom"], ""))   # 3 infos given, "" indique qu'il ny a pas d'id (cas des olds stgiaires)
            
            # 'formul' indique l'origine, ici 'formulaire de satisfaction'
            open_form("Mail_subject_attach_txt",  liste_email, 'stagiaire_tous') 

    def button_export_xls_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.liste_stagiaires = app_tables.stagiaires_inscrits.search(
                                                                tables.order_by("name", ascending=True),
                                                                numero=self.item['numero'])
        # saisie du mail posible
        self.column_panel_mail.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.text_box_mail.text = ""
        self.button_ok.visible = False
        self.column_panel_mail.visible = False

    def button_ok_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.mail = self.text_box_mail.text
        result = Mail_valideur.is_valid_email(self.mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            alert("Le mail n'a pas le bon format !")
            self.text_box_mail.focus()
            return
        # envoi vers pi5 par uplink du num_stage et de la liste des stagiaires
        # module python sur Pi5, répertoire /mnt/ssd-prog/home/jmm/AMS_data/uplinks/export-excel/export_uplink.py
        message = anvil.server.call('export_xls', self.item['numero'], self.item['code_txt'], self.item['date_debut'] , self.liste_stagiaires, self.mail)
        alert(message)

    def text_box_mail_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_ok.visible = True

    def text_box_mail_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_ok_click()

    def text_box_mail_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_mail.placeholder = ""

    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ...Visu_trombi import Visu_trombi
        open_form('Visu_trombi',self.item['numero'], self.item['code_txt'], False, None, False)

    def button_attestations_click(self, **event_args):
        """This method is called when the button is clicked"""
        liste_stagiaires = app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True),
            numero=self.item['numero'])
        if liste_stagiaires:
            result = anvil.server.call("pdf_reading", self.item, liste_stagiaires)    # Stage, stagiaires_rows
            alert(result)

    def file_loader_diplomes_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        result, erreur = anvil.server.call('sov_diplomes',self.item, file)
        if result is True :
            alert("Fichier pdf des diplomes enregisté !")
            self.button_attestations.visible = True
        else :
            alert(erreur)
