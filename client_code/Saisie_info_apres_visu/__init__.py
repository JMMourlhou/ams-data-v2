from ._anvil_designer import Saisie_info_apres_visuTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

stagiaire = None

global user
user = anvil.users.get_user()  # Acquisition de l'utilisateur (pour le role)

class Saisie_info_apres_visu(Saisie_info_apres_visuTemplate):
    def __init__(self, mel, num_stage=0, intitule="", **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.num_stage = num_stage
        self.intitule = intitule
        self.mel = mel
        
        # Any code you write here will run before the form opens.
        self.f = get_open_form()   # récupération de la forme mère pour revenir ds la forme appelante
        print("form mère atteingnable (en modif): ", self.f) 
        
        # Drop down mode de financemnt
        self.drop_down_fi.items = [(r['intitule_fi'], r) for r in app_tables.mode_financement.search()]

        # lecture sur le mail du stagiaire après click sur trombi
        stagiaire=app_tables.users.get(email=self.mel)
        
        if stagiaire:
            self.text_box_id.text = "Id = "+ str(stagiaire.get_id())
            self.text_box_mail.text = stagiaire['email']
            if stagiaire['nom'] is not None :
                nm = stagiaire["nom"].capitalize()
                nm = nm.strip()
                self.text_box_nom.text = nm
           
            if stagiaire['prenom'] is not None:
                pn = stagiaire["prenom"].capitalize()
                pn = pn.strip()
                self.text_box_prenom.text =  pn        
                
            #self.image_photo.source =                stagiaire["photo"]
            if stagiaire["photo"] is not None:
                thumb_pic = anvil.image.generate_thumbnail(stagiaire["photo"], 640)
                self.image_photo.source = thumb_pic
            else:
                self.image_photo.source =            stagiaire["photo"]

            self.text_box_ville_naissance.text =     stagiaire["ville_naissance"]
            self.text_box_cp_naissance.text =        stagiaire["code_postal_naissance"]
            self.date_naissance.date =               stagiaire["date_naissance"]
            self.text_box_pays_naissance.text =      stagiaire["pays_naissance"]
            if stagiaire["pays_naissance"] is None :
                self.text_box_pays_naissance.text = "France"
            self.text_area_rue.text =                stagiaire["adresse_rue"]
            self.text_box_ville.text =               stagiaire["adresse_ville"]
            self.text_box_code_postal.text =         stagiaire["adresse_code_postal"]
            self.text_box_tel.text =                 stagiaire['tel']
            self.text_box_email2.text =              stagiaire['email2']
            self.check_box_accept_data_use.checked = stagiaire['accept_data']
            self.text_area_commentaires.text =       stagiaire['commentaires']
            
            self.text_box_role.text =                stagiaire['role']       # Le role du stagiare 
            if user['role'] == "A":                                          # si l'utilisateur est l'administrateur,je visualise le role du stagiaire
                self.text_box_email2.visible = True
                self.text_area_commentaires.visible = True
                self.text_box_role.visible = True
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
            alert("Entrez le prénom !")
            return
        if self.text_box_nom.text == "" :           # dates vides ?
            alert("Entrez le nom !")
            return
        if self.text_box_tel.text == "" :              # tel vides ?
            alert("Entrez le teléphone")
            return
        if len(self.text_box_tel.text) < 10:    # tel inf à 10 caract ?
            alert("Le numéro de teléphone n'est pas valide")
            return
        if self.check_box_accept_data_use.checked is not True:
            r=alert("Voulez-vous valider l'utilisation de vos données par AMsport ?",dismissible=False,buttons=[("oui",True),("non",False)])
            if r :   #Non, nom pas correct
                self.check_box_accept_data_use.checked = True
                return
            
        global user
        if user['role'] == "S":
            if self.date_naissance.date is None :           # dateN vide ?
                alert("Entrez la date de naissance")
                return
            if self.text_box_ville_naissance.text == "" :    # ville N vide ?
                alert("Entrez la ville de Naissance")
                return
        if user['role'] == "A":
            r = alert(
                "Voulez-vous enlever le role 'Administrateur à cet utilisateur' ?",
                dismissible=False,
                buttons=[("oui", True), ("non", False)],
            )
        if not r:  # non
                self.text_box_role.text = 'A'
       
        # lecture sur le mail du stagiaire après click sur trombi
        stagiaire=app_tables.users.get(email=self.mel)
        if stagiaire:
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
                n=Notification("Modifications enregistées !",timeout=0.5)
                n.show()
            else :
                alert("Renseignements non sauvés !", title="Erreur")
            
            # self.button_annuler_click()
        else:
            alert("Utilisateur non trouvé !", title="Erreur")
            self.button_annuler_click()

        #js.call_js('showSidebar')
    
    def text_box_role_change(self, **event_args):                                    # Role du stagiaire a changé
        """This method is called when the text in this text box is edited"""
        self.text_box_nom_change()

    def text_box_nom_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
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
        open_form(self.f)
        
        
    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.column_panel_1.scroll_into_view()

   


