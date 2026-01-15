from ._anvil_designer import RowTemplate4Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...AlertHTML import AlertHTML
from ...AlertConfirmHTML import AlertConfirmHTML

class RowTemplate4(RowTemplate4Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        # ----------------------------------------------------------------------------------------------
        # import anvil.js    # pour screen size: Si tel: 3 data grid 3 rows sinon 8 pour ordinateur
        from anvil.js import window  # to gain access to the window objec

        screen_size = window.innerWidth
        #print("screen: ", screen_size)

        if screen_size >= 650:
            self.text_box_nom_p.font_size = 18
            self.text_box_tel.font_size = 18
            self.text_box_mail.font_size = 18
        else:
            self.text_box_nom_p.font_size = 10
            self.text_box_nom_p.width = 140
            
            self.text_box_tel.font_size = 10
            self.text_box_tel.width = 140
            
            self.text_box_mail.font_size = 8
            self.text_box_mail.width = 140
        try:    
            self.text_box_nom_p.text = self.item['name'].capitalize()+" "+ self.item['user_email']["prenom"].capitalize()
        except: # prénom encore inexistant 
            self.text_box_nom_p.text = self.item['name'].capitalize()
            
        self.text_box_mail.text = self.item['user_email']['email']
        tel = self.item['user_email']['tel']
        
        try:
            if len(tel) == 10 and tel.isdigit():
                tel = f"{tel[0:2]}-{tel[2:4]}-{tel[4:6]}-{tel[6:8]}-{tel[8:10]}"
                self.text_box_tel.text = tel
        except Exception:
            tel = "Vérifier le tel"

        # Affichage reussite au stage et couleur  SI c'est un stage de type "S"
        if self.item['stage']['type_stage'] == "S" or self.item['stage']['type_stage'] == "F":
            self.check_box_reussite.checked = self.item['reussite']
        else:
            self.check_box_reussite.visible = False
            
        if self.check_box_reussite.checked is False:
            self.button_visu_diplome.visible = False
            self.button_sending_diplome.visible = False
            self.check_box_reussite.background = "red"
            self.check_box_reussite.text = "Echec"
        else:
            self.check_box_reussite.background = "green"
            self.check_box_reussite.text = "Réussite"
        # afficher le visu diplome si le diplome existe    
        if self.item['diplome'] is not None:
            self.button_visu_diplome.visible = True
            self.button_sending_diplome.visible = True
            
        self.check_box_form_satis.checked = self.item['enquete_satisf']
        self.check_box_form_suivi.checked = self.item['enquete_suivi']
        self.init_drop_down_mode_fi()  
   
    def check_box_form_satis_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # Sauvegarde du check box au cas ou l'utilisateur répond 'non'
        sov = self.check_box_form_satis.checked
        
        if self.check_box_form_satis.checked is False:
            r = AlertConfirmHTML.ask(
                "Annulation d'un ou plusieurs formulaires de SATISFACTION:",
                "ATTENTION ! Le ou les formulaire(s) du stagiaire vont être annulés.\n\nConfirmez svp !",
                style="error",
                large = True
            )
            if not r :   #non
                if sov is False: # je remets à True
                    self.check_box_form_satis.checked = True
                else:
                    self.check_box_form_satis.checked = False
                return
        stagiaire_row=self.item    # formulaire de satisf rempli T/F
        valid_1, valid_2 = anvil.server.call("init_formulaire_satis_stagiaire", stagiaire_row, self.check_box_form_satis.checked)   # module serveur "add_stagiaire"
        if valid_1 is False:
            AlertHTML.error("Erreur :",f"Erreur en modification de l'indicateur du Formulaire de satisf°:\n\n {valid_1}")
        if valid_2 == 1: # indicateur est checké, autorisation de saisir des formulaires
            AlertHTML.info("Information :","Le stagiaire peut entrer un ou plusieurs formulaires.")
        elif valid_2 is True:
            AlertHTML.success("Succès :","Un ou plusieurs formulaires ont correctement été effacés !")
        elif valid_2 == 0:
            AlertHTML.info("Information :", "Le stagiaire n'avait pas encore rempli de formulaire")
            
    def check_box_form_suivi_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # Sauvegarde du check box au cas ou l'utilisateur répond 'non'
        sov = self.check_box_form_suivi.checked
        # Si ce n'est pas un formulaire d'un tuteur (un tuteur peur refaire plusieurs années des formulaires)
        stagiaire_row=self.item   # formulaire de suivi rempli T/F
        if self.item['numero'] != 1003:
            if self.check_box_form_suivi.checked is False: 
                r = AlertConfirmHTML.ask(
                    "Annulation d'un ou plusieurs formulaires de SUIVI:",
                    "ATTENTION ! Le ou les formulaire(s) du stagiaire vont être annulés.\n\nConfirmez svp !",
                    style="error",
                    large = True
                )
            if not r :   #non
                if sov is False: # je remets à True
                    self.check_box_form_suivi.checked = True
                else:
                    self.check_box_form_suivi.checked = False
                return
            valid = anvil.server.call("init_formulaire_suivi_stagiaire", stagiaire_row, self.check_box_form_suivi.checked, True)   # on effecera le formulaire 
            if valid is True:
                AlertHTML.success("Succès :","Le formulaire a bien été effacé !\n\n Il peut être ré-entré par le stagiaire si nécessaire.")
        else: # stage 1003, tuteur de MTnoto, je peux effacer le check du formulaire de suivi car chaque année il peut le refaire pour un autre stage
            valid = anvil.server.call("init_formulaire_suivi_stagiaire", stagiaire_row, self.check_box_form_suivi.checked, False)   # False, on n'effacera pas les anciens formulaires
            if valid is True:
                AlertHTML.success("Succès :","Réinitialisation effectuée au niveau du Tuteur, Le ou les formulaires n'ont pas été effacé(s).")
        
    def init_drop_down_mode_fi(self):
        self.f = get_open_form()   # récupération de la forme mère (Stage_visu_modif) ou (Recherche_stagiaire_v3) pour revenir ds la forme appelante
        liste =[]
        for x in self.f.drop_down_mode_fi.items:
            liste.append((x[0],x[1])) 
        self.drop_down_mode_fi.items = liste
        self.drop_down_mode_fi.selected_value = self.item["financement"]

    def drop_down_mode_fi_change(self, **event_args):
        """This method is called when an item is selected"""
        # sauvegarde du mode de fi si ok 
        nom_p = self.item["name"].capitalize() + " " + self.item["prenom"].capitalize()
        r = AlertConfirmHTML.ask(
            "Mode de financement",
            f"Voulez-vous vraiment Changer le mode de financement pour {nom_p} ?",
            style="error",
            large = True
        )
        if r:  # oui
            stagiaire_row=self.item   # Changement du mode de fi
            result = anvil.server.call("modif_mode_fi_1_stagiaire", stagiaire_row, self.drop_down_mode_fi.selected_value)
            if result:
                AlertHTML.success("Succès :","Modification du mode de financemnt effectuée !")
            else:
                AlertHTML.error("Erreur :",f"Modification du mode de financemnt NON effectuée !\n\n {result}")
        else:
            self.drop_down_mode_fi.selected_value = self.item["financement"]

    def button_sending_click(self, **event_args):
        """This method is called when the button is clicked"""
        liste_email = []
        liste_email.append((self.text_box_mail.text, self.item['user_email']["prenom"].capitalize(),""))   # mail et prénom, id pas besoin
        open_form('Mail_subject_attach_txt',liste_email,"stagiaire_1")

    def button_visu_diplome_click(self, **event_args):
        """This method is called when the button is clicked"""
        pdf = self.item['diplome']
        new_file_name = f"Attestation_{self.item['stage_txt']}_{self.item['name']}_{self.item['prenom']}"
        new_file_named = anvil.BlobMedia("application/pdf", pdf.get_bytes(), name=new_file_name+".pdf")
        if pdf:
            anvil.media.download(new_file_named)
            AlertHTML.success("Succès :","Diplôme téléchargé !")
        else:
            AlertHTML.error("Erreur :","Diplôme non trouvé !")

    def check_box_reussite_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        # envoie en modif
        if self.check_box_reussite.checked is False:
            self.check_box_reussite.background = "red"
            self.button_visu_diplome.visible = False
            self.button_sending_diplome.visible = False
            self.check_box_reussite.text = "Echec"
        else:
            self.check_box_reussite.background = "green"
            self.check_box_reussite.text = "Réussite"
            # afficher le visu diplome si le diplome existe    
            if self.item['diplome'] is not None:
                self.button_visu_diplome.visible = True   
                self.button_sending_diplome.visible = True
            
        valid = anvil.server.call("maj_reussite", self.item, self.check_box_reussite.checked) 
        if valid :
            AlertHTML.success("Succès :","Maj effectuée !")
        else :
            AlertHTML.error("Erreur :",valid)

    def button_sending_diplome_click(self, **event_args):
        """This method is called when the button is clicked"""
        # création de la row du stagiaire qui contient le diplome en colonne 'diplome'
        r=alert(f"Envoi du diplôme à {self.item['prenom'].capitalize()} ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            # get() renvoie directement une row unique ou None, donc j'évite de manipuler les listes.
            liste_stagiaire = app_tables.stagiaires_inscrits.get(
                reussite=True,
                numero=self.item['numero'],
                user_email=self.item['user_email'])
            
            if not liste_stagiaire:
                alert("Ce stagiaire n'a pas eu de succès à son examen !")
                return
    
            if liste_stagiaire:    # uplink PI5
                result = anvil.server.call("one_pdf_reading", self.item['stage'], liste_stagiaire)    # Stage_row, row du stagiaire, option envoi d'un seul diplome
                if result == "OK":
                    alert(f"Diplôme {self.item['stage_txt']} bien envoyé à {self.item['prenom'].capitalize()} {self.item['name'].capitalize()} !")
                else:
                    alert(result)

    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        r = AlertConfirmHTML.ask(
            "Retrait d'un stagiaire :",
            "Enlever ce stagiaire de ce stage ?",
            style="error",
            large = True
        )
        if r :   #oui   
            stagiaire_row = self.item['user_email']
            stage_num = self.item['numero']
            txt_msg = anvil.server.call("del_stagiaire", stagiaire_row, stage_num)   # module serveur "add_stagiaire"
            AlertHTML.success("Succès :",txt_msg)
            # réaffichage par initialisation de la forme mère 
            id=self.item['stage'].get_id()
            open_form('Stage_visu_modif', self.item['numero'], id) # réinitialisation de la fenêtre

    def text_box_nom_p_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        mel = self.item['user_email']['email']  
        num_stage = self.item["stage"]['numero']
        from ...Saisie_info_apres_visu import Saisie_info_apres_visu
        open_form('Saisie_info_apres_visu', mel, num_stage, intitule="")

    def text_box_mail_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_nom_p_focus()

    def text_box_tel_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_nom_p_focus()
        


        
