from ._anvil_designer import Saisie_info_de_baseTemplate
from anvil import *

import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Mail_valideur  # pour test du mail format 
from .. import French_zone   #pour tester la date de naissance
from datetime import datetime
from datetime import timedelta
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML

global user
user=anvil.users.get_user()

class Saisie_info_de_base(Saisie_info_de_baseTemplate):
    def __init__(self, first_entry=False, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run before the form opens.
        self.first_entry = first_entry
        if first_entry is True:
            self.button_retour.visible = False
            
        global user
        user=anvil.users.get_user()
        # Si col temp en table user contient un chiffre, le user sera inscrit dans le stage correspondant ...
        #  ...  qd il entrera dans l'app pour la 1ere fois
        self.stage=str(user['temp'])

        try:
            if int(self.stage) > 998:
                self.column_panel_naissance.visible = False
                self.column_panel_adresse.visible = False
                self.drop_down_fi.visible = False
                self.column_panel_mail2_commentaires.visible = False
        except:
            pass
        
        # Drop down mode de financemnt
        self.drop_down_fi.items = [(r['intitule_fi'], r) for r in app_tables.mode_financement.search()]

        if user:
            self.row_id = user.get_id()   # Récup du row_id de la fiche du stagiaire
            self.text_box_mail.text =  user['email']
            if user["nom"] is not None:
                nm = user["nom"]
                nm = nm.strip()
                nm = nm.capitalize()
                self.text_box_nom.text = nm
                
            self.text_box_prenom.text =  user['prenom']

            #self.image_photo.source =                user["photo"]
            if user["photo"] is not None:
                thumb_pic = anvil.image.generate_thumbnail(user["photo"], 640)
                self.image_photo.source = thumb_pic
            else:
                self.image_photo.source =            user["photo"]

            self.text_box_v_naissance.text =         user["ville_naissance"]
            self.text_box_c_naissance.text =         user["code_postal_naissance"]
            self.date_naissance.date =               user["date_naissance"]
            self.text_box_pays_naissance.text =      user["pays_naissance"]
            if user["pays_naissance"] is None :
                self.text_box_pays_naissance.text = "France"
            self.text_area_rue.text =                user["adresse_rue"]
            self.text_box_ville.text =               user["adresse_ville"]
            self.text_box_code_postal.text =         user["adresse_code_postal"]
            self.text_box_tel.text =                 user['tel']
            self.text_box_email2.text =              user['email2']
            self.check_box_accept_data_use.checked = user['accept_data']
            self.text_area_commentaires.text =       user['commentaires']
            
            #affiche mail2 et commentaires si Admin, Bureaux, formateur
            if user['role'] != "S" and user['role']!="T" and user['role']!="V":   
               self.text_box_email2.visible = True
               self.text_area_commentaires.visible = True
        else: # Admin ou Formateur ou Bureaux 
            self.button_retour_click()

    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        #self.image_photo.source = file
        thumb_pic = anvil.image.generate_thumbnail(file, 640)
        self.image_photo.source = thumb_pic
        self.button_validation.visible = True

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        global user
        if self.text_box_prenom.text == "" :           # dates vides ?
            AlertHTML.error("Oublie !", "Entrez votre Prénom !")
            return
        else:
            pn = self.text_box_prenom.text
            pn = pn.capitalize()
            pn = pn.strip()
            self.text_box_prenom.text =  pn  
        
        if self.text_box_nom.text == "" :           # dates vides ?
            AlertHTML.error("Oublie !", "Entrez votre Nom de Famille !")
            return
        else:
            n = self.text_box_nom.text
            n = n.capitalize()
            n = n.strip()
            self.text_box_nom.text =  n  

        if self.image_photo.source is None:
            AlertHTML.error("Oublie !", "Entrez votre Photo !")
            return
            
        if self.text_box_tel.text == "":    # tel vides ou inf à 10 caract ?
            AlertHTML.error("Oublie !", "Entrez votre numéro de Tel !")
            return
        if len(self.text_box_tel.text) < 10:    # tel inf à 10 caract ?
            AlertHTML.error("Erreur !", "Le num de Tel doit avoir 10 caractères !")
            return   
            
        # Si Inscription ds un stage numéro > 998 : F ou T ou QCM: pas de test sur Naissance et adresse     
        if int(self.stage) < 998:
            # naissance non vide, supérieure à 15 ans
            if self.date_naissance.date is None :           # dateN vide ?
                AlertHTML.error("Oublie !", "Entrez la date de Naissance !")
                return   
            now=French_zone.french_zone_time()   # now est le jour/h actuelle (datetime object)
            now=now.date()                       # extraction de la date, format yyyy-mm-dd
            #alert(f"now: {now}")
            date_n=self.date_naissance.date      # extraction de la date de naissance saisie format yyyy-mm-dd
            #alert(f"date_N: {date_n}")
            span = now - date_n                  # calcul diff des dates en jours
            #alert(f"écart: {span}")
            #alert(f"écart: {type(span)}")
            span_years = span.days/365
            #alert(f"écart: {span_years}")
            if span_years < 15:
                AlertHTML.error("Age trop jeune !", "Erreur sur la date de naissance !")
                return   

            if self.text_box_v_naissance.text == "" :    # ville N vide ?
                AlertHTML.error("Ville de Naissance oubliée!", "Entrez votre ville de naissance !")
                return   
            if len(self.text_box_v_naissance.text)<3:
                AlertHTML.error("Ville de Naissance incomplète !", "Entrez votre Ville de Naissance !")
                return 
                
            # Test sur Code postal NAISSANCE, non vide, 5 caractères numériques.
            if self.text_box_c_naissance.text == "":
                AlertHTML.error("Code Postal de la Ville de Naissance :", "Entrez votre Code Postal de naissance !\n\n Si vous êtes né à l'étranger, entrez 99999")
                return
                
            
            if self.text_area_rue.text == "":
                alert("Entrez votre Rue !")
                return  
            if len(self.text_area_rue.text)<5:
                alert("La Rue est incomplète !")
                return 
                
            if self.text_box_ville.text == "":
                alert("Entrez votre Ville (adresse postale) !")
                return
            if len(self.text_box_ville.text)<3:
                alert("La Ville (adresse postale) est incomplète !")
                return 
                
            # Test sur Code postal adresse, non vide, 5 caractères numériques.
            if self.text_box_code_postal.text == "":
                alert("Entrez votre Code Postal (adresse postale) !")
                return
         
            if len(self.text_box_code_postal.text) != 5:
                alert("Le Code Postal (adresse postale) doit être de 5 chiffres !")
                return
                
            try:
                cp_test = int(self.text_box_code_postal.text)
            except:
                alert("Le Code Postal (adresse postale) ne doit contenir que des chiffres !")
                return  
                
            # Stage non type formateur: Si mode de financemt non sélectionné alors que 1ere saisie de la fiche renseignemnt
            if self.drop_down_fi.selected_value is None and self.first_entry is True: 
                alert("Vous devez sélectionner un mode de financement !")
                return

        
        if self.check_box_accept_data_use.checked is not True:
            r = AlertConfirmHTML.ask(
                "RGPD: ",
                "<p>Voulez-vous valider l'utilisation de vos données par AMsport ?</p>",
                style="info",
                large = True
            )
            if r:  # oui
                self.check_box_accept_data_use.checked = True
                return

        # TEST Mail format & MAIL EXISTE DEJA ? (il a peut être été modifié):
        # 1-Test mail au bon format ?
        # Mail format validation
        mail = self.text_box_mail.text.lower()
        result = Mail_valideur.is_valid_email(mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            alert("Le mail n'a pas le bon format !")
            self.text_box_mail.focus()
            return
            
        # 2- Je lis le user selon le mail entré dans self.text_box_mail
        try:
            test = app_tables.users.get(email=self.text_box_mail.text)
            if test:  # un mail existe déjà en table user, est-ce bien cet utisateur ?  
                row_id2 = test.get_id()
                if self.row_id != row_id2: # 2 id pour le même mail !
                    
                    alert("Le mail entré existe déjà dans la base de données !")
                    return
        except Exception as e:
            AlertHTML.error("Erreur: ", f"Erreur en relecture du user sur mail entré !\n {e}")
            alert(f"Erreur en lecture du mail entré !\n {e}")
            return
        
        if user:
            result = anvil.server.call("modify_users", user,
                                                    self.text_box_nom.text,
                                                    self.text_box_prenom.text,
                                                    self.image_photo.source,
                                                    self.text_box_v_naissance.text,
                                                    self.text_box_c_naissance.text,
                                                    self.date_naissance.date,
                                                    self.text_box_pays_naissance.text,
                                                    self.text_area_rue.text,
                                                    self.text_box_ville.text,
                                                    self.text_box_code_postal.text,
                                                    self.text_box_tel.text,
                                                    self.text_box_email2.text,
                                                    self.check_box_accept_data_use.checked,
                                                    self.text_area_commentaires.text
                                                    )
            if result is True :
                #alert("Renseignements enregistés !")    # *************************************
                # insertion du stagiaire automatiqt si num_stage != 0
                if user and self.first_entry:          # 1ERE ENTREE 
                    if  user['temp']==0:
                        AlertHTML.success("Succès", "Renseignements enregistés !,\n Vous n'êtes pas inscrit à un stage.")
                        #alert("Renseignements enregistés !,\n Vous n'êtes pas inscrit à un stage.")
                        self.button_retour_click()
                    else:
                        code_fi = "???"
                        if user['temp'] < 998:
                            row = self.drop_down_fi.selected_value
                            code_fi=row['code_fi']
                        if user['temp'] == 1003:       # si tuteur, chercher ds user['temp_for_stage'] pour quel stage travaille le tuteur
                            pour_stage = user['temp_for_stage']
                            #print(f"++++++++++++++++++++++++++ 1003 pour stage: {pour_stage}")
                        else:
                            pour_stage = 0
                        
                        txt_msg = anvil.server.call("add_stagiaire", user, self.stage, code_fi, "", pour_stage)
                        alert(txt_msg)
                        anvil.users.logout()
                        AlertHTML.success("info", "Vous devriez créer un raccourci pour cette application !")
                        self.button_retour_click()
            else :
                AlertHTML.error("Erreur: ", "Fiche de renseignements non enregistée !")
                self.button_retour_click()
        else:
            AlertHTML.error("Erreur:", "Utilisateur non trouvé !")
            
    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 
        

        #js.call_js('showSidebar')
        
    
    
    def text_box_nom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True
        self.button_validation_copy.visible = True

    def text_box_prenom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_tel_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_mail_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def date_naissance_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.text_box_nom_change()

    def text_box_ville_naissance_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_cp_naissance_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_pays_naissance_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_area_rue_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.text_box_nom_change()

    def text_box_ville_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_code_postal_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_email2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_area_commentaires_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.text_box_nom_change()

    def drop_down_fi_change(self, **event_args):
        """This method is called when an item is selected"""
        self.text_box_nom_change()


 
            














            

        

