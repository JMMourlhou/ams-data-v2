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
from InputBox.input_box import InputBox, alert2, input_box
#import anvil.js    # pour screen size
from anvil.js import window # to gain access to the window object
global screen_size
screen_size = window.innerWidth

class RowTemplate3(RowTemplate3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

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
            
            #self.text_box_2.text = self.item['code']['code']

    # récupération par l'event:
    def text_box_3_click(self, **event_args):   # Click sur date
        """This method is called when the button is clicked"""
        self.text_box_1_click()
        
    def text_box_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        num_stage = int(self.text_box_1.text)
        open_form('Stage_visu_modif', num_stage)   
        
    def text_box_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.text_box_1_click()

    def button_inscription_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert2('Si vous voulez effectuer une **inscription**:\n\n'
               '```\n'
               '1- Cliquez sur "Oui"\n'
               '2- Recherchez le stagiaire\n'
               '   à inscrire\n'
               '3- Cliquez sur son nom\n'
                '```\n' 
                ,
                buttons=['Oui', 'Non'],
                default_button='Oui',     # si press return=Oui
                large=True
                )
        if r== "Oui" :   
            from ...Recherche_stagiaire import Recherche_stagiaire
            num_stage = self.text_box_1.text        
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
            result = anvil.server.call('del_stage',self.item['numero'])
            if result is True:
                alert("Stage annulé !")
                open_form('Visu_stages')
            else:
                alert("Stage non trouvé, annulation impossible")
        else:
            alert("Ce stage contient des stagiaires, vous ne pouvez pas l'annuler !")    

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
        liste_stagiaires = app_tables.stagiaires_inscrits.search(
                                                                tables.order_by("name", ascending=True),
                                                                numero=self.item['numero'])
        # envoi vers pi5 par uplink du mail saisi 
        mail = "jmmourlhou@gmail.com"
        result = anvil.server.call('get_mail_dest', mail)
        if result is False:
            alert("Le mail n'a pas le bon format !")
            return
            
        # envoi vers pi5 par uplink du num_stage et de la liste des stagiaires
        message = anvil.server.call('export_xls', self.item['numero'], self.item['code_txt'], self.item['date_debut'] , liste_stagiaires, "jmmourlhou@gmail.com")
        alert(message)
  


