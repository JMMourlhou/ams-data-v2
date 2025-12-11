from ._anvil_designer import Saisie_info_apres_visuTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Mail_valideur  # pour test du mail format 
from .. AlertHTML import AlertHTML
from .. AlertConfirmHTML import AlertConfirmHTML

class Saisie_info_apres_visu(Saisie_info_apres_visuTemplate):
    def __init__(self, mel, num_stage=0, intitule="", row_id=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.user = anvil.users.get_user()  # Acquisition de l'utilisateur (pour le role)
        self.num_stage = num_stage
        self.intitule = intitule
        self.mel = mel
        self.row_id = row_id
        
        # Any code you write here will run before the form opens.
        self.f = get_open_form()   # récupération de la forme mère pour revenir ds la forme appelante
        #print("form mère atteingnable (en modif): ", self.f) 
        
        # Drop down mode de financemnt
        self.drop_down_fi.items = [(r['intitule_fi'], r) for r in app_tables.mode_financement.search()]
        if row_id is None:
            # lecture sur le mail du stagiaire après click sur trombi
            self.stagiaire=app_tables.users.get(email=self.mel)
        else: 
            self.stagiaire=app_tables.users.get_by_id(self.row_id)
        
        if self.stagiaire:
            self.id_fiche_stagiaire = self.stagiaire.get_id()
            self.text_box_id.text = "Id = "+ str(self.id_fiche_stagiaire)
            self.text_box_mail.text = self.stagiaire['email']
            if self.stagiaire['nom'] is not None :
                nm = self.stagiaire["nom"].capitalize()
                nm = nm.strip()
                self.text_box_nom.text = nm
           
            if self.stagiaire['prenom'] is not None:
                pn = self.stagiaire["prenom"].capitalize()
                pn = pn.strip()
                self.text_box_prenom.text =  pn        
                
            #self.image_photo.source =                stagiaire["photo"]
            if self.stagiaire["photo"] is not None:
                thumb_pic = anvil.image.generate_thumbnail(self.stagiaire["photo"], 640)
                self.image_photo.source = thumb_pic
            else:
                self.image_photo.source =            self.stagiaire["photo"]

            self.text_box_ville_naissance.text =     self.stagiaire["ville_naissance"]
            self.text_box_cp_naissance.text =        self.stagiaire["code_postal_naissance"]
            self.date_naissance.date =               self.stagiaire["date_naissance"]
            self.text_box_pays_naissance.text =      self.stagiaire["pays_naissance"]
            if self.stagiaire["pays_naissance"] is None :
                self.text_box_pays_naissance.text = "France"
            self.text_area_rue.text =                self.stagiaire["adresse_rue"]
            self.text_box_ville.text =               self.stagiaire["adresse_ville"]
            self.text_box_code_postal.text =         self.stagiaire["adresse_code_postal"]
            self.text_box_tel.text =                 self.stagiaire['tel']
            self.text_box_email2.text =              self.stagiaire['email2']
            self.check_box_accept_data_use.checked = self.stagiaire['accept_data']
            self.text_area_commentaires.text =       self.stagiaire['commentaires']
            
            self.text_box_role.text =                self.stagiaire['role']       # Le role du stagiare 
            
            if self.user['role'] == "A":      # si l'utilisateur est l'administrateur,je visualise le role du stagiaire
                self.text_box_email2.visible = True
                self.text_area_commentaires.visible = True
                self.text_box_role.visible = True
            else: # l'utilisateur n'est pas l'admin
                self.text_box_role.visible = False
        else:
            self.button_annuler_click()


    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        #self.image_photo.source = file
        thumb_pic = anvil.image.generate_thumbnail(file, 640)
        self.image_photo.source = thumb_pic
        self.button_validation.visible = True
        self.button_validation_copy.visible = True
        

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.text_box_prenom.text == "" :           # dates vides ?
            AlertHTML.error("Erreur :", "Entrez le Prénom !")
            return
        if self.text_box_nom.text == "" :           # dates vides ?
            AlertHTML.error("Erreur :", "Entrez le Nom !")
            return
        if self.text_box_tel.text == "" :              # tel vides ?
            AlertHTML.error("Erreur", "Entrez le Téléphone !")
            return
        if len(self.text_box_tel.text) < 10:    # tel inf à 10 caract ?
            AlertHTML.error("Erreur :", "Le numéro de teléphone n'est pas valide !")
            return
        if self.check_box_accept_data_use.checked is not True:
            r = AlertConfirmHTML.ask("RGPD: ", "<p>Voulez-vous valider l'utilisation de vos données par AMsport ?</p>", style="info", large = True)
            if r :   #Non, nom pas correct
                self.check_box_accept_data_use.checked = True
                return
            
        if self.user['role'] == "S":
            if self.date_naissance.date is None :           # dateN vide ?
                AlertHTML.error("Erreur :", "Entrez la date de Naissance !")
                return
            if self.text_box_ville_naissance.text == "" :    # ville N vide ?
                AlertHTML.error("Erreur :", "Entrez la ville de Naissance !")
                return
                
        # Test sur Code postal NAISSANCE, non vide, 5 caractères numériques.
        if self.text_box_cp_naissance.text == "" or len(self.text_box_cp_naissance.text)!=5:
            AlertHTML.error("Code Postal de la Ville de Naissance :", "Entrez le Code Postal de naissance exacte!<br><br> Si vous êtes né à l'étranger, entrez 99999")
            return
        
        # il y a eu un changement du role de l'admin au cours de la maj de cette fiche         
        if self.user['role'] == "A" and self.stagiaire['role'] == "A" and self.text_box_role.text != "A":    # L'utilisateur est l'admin et il traite sa propre fiche
            r = alert(
                "Voulez-vous enlever le role 'Administrateur à cet utilisateur' ?",
                dismissible=False,
                buttons=[("oui", True), ("non", False)],
            )
            if not r:  # non
                self.text_box_role.text = 'A'
        
        # Deux tests sur le mail: Mail format & MAIL EXISTE DEJA ? (il a peut être été modifié):
        
        # 1-Test mail au bon format ?
        # Mail format validation
        mail = self.text_box_mail.text.lower()
        result = Mail_valideur.is_valid_email(mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            AlertHTML.error("Erreur :", "Le mail n'a pas le bon format !")
            self.text_box_mail.focus()
            return
            
        # 2- TEST SI MAIL EXISTE DEJA (il a peut être été modifié):
        # Je lis le user selon le mail entré dans self.text_box_mail
        test = app_tables.users.get(email=self.text_box_mail.text)
        if test:
            row_id2 = test.get_id()
            if self.id_fiche_stagiaire != row_id2: # 2 id pour le même mail !
                AlertHTML.error("Erreur :", "Le mail entré existe déjà dans la base de données !")
                return
            
        if self.stagiaire:
            result = anvil.server.call("modify_users_after_trombi", self.mel,
                                                    self.text_box_mail.text,
                                                    self.text_box_nom.text,
                                                    self.text_box_prenom.text,
                                                    self.image_photo.source,
                                                    self.text_box_ville_naissance.text,
                                                    self.text_box_cp_naissance.text,
                                                    self.date_naissance.date,
                                                    self.text_box_pays_naissance.text,
                                                    self.text_area_rue.text,
                                                    self.text_box_ville.text,
                                                    self.text_box_code_postal.text,
                                                    self.text_box_tel.text,
                                                    self.text_box_email2.text,
                                                    self.check_box_accept_data_use.checked,
                                                    self.text_area_commentaires.text,
                                                    self.text_box_role.text
                                                    )
            if result is True :
                self.button_validation_copy.visible = False
                self.button_validation.visible = False
                n=Notification("Modifications enregistées !",timeout=2)
                n.show()
            else :
                AlertHTML.error("Erreur :", f"Renseignements non sauvés !\n {result}")
            
            # self.button_annuler_click()
        else:
            AlertHTML.error("Erreur :", "Utilisateur non trouvé !")
            self.button_annuler_click()

    
    def text_box_role_change(self, **event_args):                                    # Role du stagiaire a changé
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_nom_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_validation.visible = True
        self.button_validation_copy.visible = True


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

    def check_box_accept_data_use_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.text_box_nom_change()

    def button_download_photo_click(self, **event_args):
        """This method is called when the button is clicked"""
        "lecture du media object que j'ai stocké en server module ds table stages, ligne du stage"
        # lecture sur le mail du stagiaire après click sur trombi
        stagiaire=app_tables.users.get(email=self.mel)
        if not stagiaire:
            print("stagiaire non trouvé à partir de son mail en saisie après trombi")
        else:
            if self.image_photo.source is not None:
                anvil.media.download(stagiaire['photo'])
                alert("Photo téléchargée")

    def button_annuler_copy_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_annuler_click()
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Je connais la forme appelante: en init : self.f = get_open_form()
        if self.button_validation.visible is not True: # si pas de changements
            open_form(self.f)
        else:
            open_form("Visu_stages")
        
    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.column_panel_1.scroll_into_view()

    def button_qcm_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_histo_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def button_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        liste_email = []
        liste_email.append((self.text_box_mail.text,self.text_box_prenom.text,""))   # mail et prénom, id pas besoin
        open_form('Mail_subject_attach_txt',liste_email,"stagiaire_1")

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Effacement du stagiaire/formateur si pas ds un stage et si je suis l'administrateur
        user = anvil.users.get_user()
        if user["role"] == "A" or user["role"]=="B":   # seul,l'administrateur et bureaux peuvent effacer definitivement un stagiaire ou formateur ou tuteur
            # Cette personne est-elle inscrite ds un ou plusieurs stages ?
            list = app_tables.stagiaires_inscrits.search(user_email=self.stagiaire)
            detail =""
            for stage in list:
                detail=detail+str(stage['numero'])+" "

            nb_stages = len(list)
            if nb_stages != 0:
                txt="stage"
                if nb_stages > 1:
                    txt = "stages"
                alert(f"Effacement impossible:<br>Cette personne est inscrite dans {nb_stages} {txt}<br><br>Détail:<br>{txt} N°{detail}")
                self.button_histo_click()   # visu de l'histo du stagiaire
                return
            # Effact de la personne si confirmation
            r=alert("Voulez-vous vraiment enlever définitivement cette personne ? ",dismissible=False ,buttons=[("oui",True),("non",False)])
            if r :   # oui
                # lecture row users
                if self.stagiaire:
                    txt_msg = anvil.server.call("del_personne",self.stagiaire)
                alert(txt_msg)
                open_form("Recherche_stagiaire_v3")
            else:
                return

    

   


