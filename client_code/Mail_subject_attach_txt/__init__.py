from ._anvil_designer import Mail_subject_attach_txtTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media


# emails_liste liste des mails
# ref_model contient lea ref du modele de mail si vient de qcm ou formul satisf ou recherche etc...du permet de court circuiter la drop down du choix du modèle 
class Mail_subject_attach_txt(Mail_subject_attach_txtTemplate):
    def __init__(self, emails_liste=[], ref_model = "", old_stagiaires = False, **properties): 
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()
        self.old_stagiaires = old_stagiaires
        
         # Récupération des icones ds files pour afficher les icones en template 16
        self.icone_xls = app_tables.files.get(path="logo_xls.jpg")['file'] # lit la colonne 'file', media object
        self.icone_doc = app_tables.files.get(path="logo word.jpg")['file']
        self.icone_ppt = app_tables.files.get(path="logo_ppt.jpg")['file']
        self.icone_pdf = app_tables.files.get(path="logo pdf.jpg")['file']
        
        self.dico_attachements = {}                # initialisation du dict des attachements
        self.list_attach = []          # initialisation de la liste des attachements
    
        self.ref_model = ref_model
        print('ref_model: ',self.ref_model)   
      
        self.mode_creation = False

        self.label_ref_model.text = ref_model # sauve la ref de modèle de mail
        
        self.emails_liste = emails_liste # liste des mails
        print('emails liste: ', self.emails_liste)
        self.label_emails_liste.text = emails_liste   # sauve la liste de mails à envoyer, (utilisé ds le item repeating panel, del)

        
        # import anvil.js    # pour screen size
        from anvil.js import window  # to gain access to the window object

        global screen_size
        screen_size = window.innerWidth

        # INITIALISATION Drop down   drop_down_type_mails
        self.drop_down_type_mails.items = [(r['type_mail'], r) for r in app_tables.mail_type.search(tables.order_by("type_mail", ascending=True))]
        
        # ref_model en init contient la ref du modele si vient de qcm ou formul etc...du permet de court circuiter la drop down du choix du modèle 
        if self.ref_model != "":
            # lecture du modele pour court circuiter la drop down du choix du modèle 
            type_mail_row = app_tables.mail_type.get(ref=self.ref_model)
            #print("ok: ", type_mail_row['type_mail'])
            if type_mail_row:
                self.drop_down_type_mails.selected_value = type_mail_row
                self.drop_down_type_mails_change(type_mail_row)

    def drop_down_type_mails_change(self, type_mail_row=None, **event_args): 
        #si j'ai court circuiter le dropdown (car vient de qcm, form satisf, recherche stag, ...) 
        if type_mail_row is None:
            type_mail_row = self.drop_down_type_mails.selected_value
            #self.ref_model = type_mail_row['ref']
            
        liste_mails =  app_tables.mail_templates.search(
                                                        tables.order_by("mail_subject", ascending=True),
                                                        type = type_mail_row
                                                        )
        self.repeating_panel_1.visible = True
        self.repeating_panel_1.items = liste_mails
        #for mail in liste_mails:
        #    self.column_panel_content.add_component(Mail_model(mail['mail_subject'], mail['mail_text'], mail.get_id(), self.ref_model, self.emails_liste))

        self.column_panel_detail.visible = False
        self.file_loader_attachments.visible = True
        self.button_sending.visible = True
        self.button_new.visible = True
        self.button_annuler.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f) 

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.mode_creation is True:  # Création du modèle
            if not self.drop_down_type_mails.selected_value:
                alert("Sélectionnez le type de modèle")
                return
            #r=alert("Enregistrer ce modèle ?",buttons=[("oui",True),("non",False)])
            #if r :   # Oui               
            result = anvil.server.call('add_mail_model', self.drop_down_type_mails.selected_value,self.text_box_subject_detail.text, self.text_area_text_detail.text)
        else:   # Modif du modèle
            #r=alert("Modifier ce modèle ?",buttons=[("oui",True),("non",False)])
            #if r :   # Oui               
            result = anvil.server.call('modify_mail_model',self.label_id.text,self.text_box_subject_detail.text, self.text_area_text_detail.text)
        if not result:
            if self.mode_creation is True:  # Création du modèle
                alert("Modèle de mail non créé")
            else:
                alert("Modèle de mail non modifié")
        else:
            if self.mode_creation is True:  # Création du modèle
                alert("Modèle de mail créé")
            else:
                alert("Modèle de mail modifié")      
        #self.drop_down_type_mails_change()
        self.column_panel_detail.visible = False   # effact du panel de création/modif
        self.button_modif.visible = False
        self.file_loader_attachments.visible = True

        self.drop_down_type_mails_change(self.drop_down_type_mails.selected_value)

    def button_sending_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Confirmez-vous l'envoi ?",dismissible=False, buttons=[("oui",True),("non",False)])
        if r :   # Oui    
            liste_des_attachements = list(self.dico_attachements.keys()) # extraction des clefs du dico des attachements
            """
            print("Avant envoi server pour mailing")
            print("email liste:",self.emails_liste)
            print("subject:",self.text_box_subject_detail.text)
            print("texte: ",self.text_area_text_detail.text)
            """

            self.task_mail = anvil.server.call("run_bg_task_mail",self.emails_liste, self.text_box_subject_detail.text, self.text_area_text_detail.text, liste_des_attachements, self.old_stagiaires)
            self.timer_1.interval=0.5
            

    def text_box_subject_detail_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_modif.visible = True
        
    def text_area_text_detail_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.text_box_subject_detail_change()

    def button_new_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        self.column_panel_detail.visible = True # panel création visible
        self.repeating_panel_1.visible = False      # panel des modèles invisible
        self.repeating_panel_2.visible = False      # panel des attachements invisible
        self.file_loader_attachments.visible = False
        self.button_sending.visible = False
        self.mode_creation = True
        self.text_box_subject_detail.text = ""
        self.text_area_text_detail.text = ""
        

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Abandon en création ou modif de modèle
        self.button_annuler.visible = True
        self.button_new.visible = True
        self.column_panel_detail.visible = False # cache la form création/modif de modèle
        self.repeating_panel_1.visible = True # remontre les modèles 

    def file_loader_attachments_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""

        if file is not None:  #pas d'annulation en ouvrant choix de fichier
            self.list_attach = [] # réinitialisation de la liste pour le repeating panel
            # insertion ds le dictionaire liste_attachements et création de la liste correspondante pour le repeating panel
            
            
            clef = file         # media object du fichier est la clé du dict 
            valeur = file.name   # valeur est le nom du dict
            print("clef: ",clef, "     valeur: ", valeur)
            self.dico_attachements[clef] = valeur   # je mets à jour le dico des attachements media_file : file_name_txt

            for clef, valeur in self.dico_attachements.items():
                self.list_attach.append((clef,valeur))  # transformation dict en liste pour le repeating panel
            
            #affichage image
            self.repeating_panel_2.visible = True
            self.repeating_panel_2.items = self.list_attach

    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        try:
            if self.task_mail.is_completed():
                self.timer_1.interval=0
                anvil.server.call('task_killer',self.task_mail)

                # lit le nb de mails ds table temp
                nb_mails = app_tables.temp.search()[0]['nb_mails_sent']
                if nb_mails == 1:
                    msg = "1 mail envoyé"
                else:
                    msg = str(nb_mails)+" mails traités"
                alert(msg)
            self.button_retour_click()
        except:
            pass
       
        