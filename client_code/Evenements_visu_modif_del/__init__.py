from ._anvil_designer import Evenements_visu_modif_delTemplate
from anvil import *

import anvil.users
import anvil.server

import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import French_zone  # pour afficher la date du jour
from datetime import datetime

# Visu, Modif, Del d'un évenement ou d'un incident
# type_evnt = ROW de table Event_types permet de réafficher les évenemnts après un effact d'un evnt (type_evnt != None)
class Evenements_visu_modif_del(Evenements_visu_modif_delTemplate):
    def __init__(self, type_evnt_row=None ,**properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.id = None
        self.data_grid_1.visible = False
        self.check_box_visu_erreurs.visible = False
        
        # envoi direct en traitement du drop down evenement si vient d'un effacement ou modif d'évenement
        if type_evnt_row is not None:
            self.drop_down_event.selected_value = type_evnt_row
            self.drop_down_event_change()
        # acquisition de l'heure
        self.now = (French_zone.french_zone_time())  # now est le jour/h actuelle (datetime object)
        
        # initilisation Drop down codes type évenements
        liste_event = []
        for r in app_tables.event_types.search(tables.order_by("code", ascending=True)):
            liste_event.append((r['msg_1'],r))   # on prend tous les msg: nouvel evnt, voir ...
        self.drop_down_event.items = liste_event
        """
        for type in self.drop_down_event.items:
            print(type, type[0], type[1])
        """
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form("Main", 99)

    def drop_down_event_change(self, **event_args):
        """This method is called when an item is selected"""
    
        # Acquisition du choix d'évenements à afficher
        self.text_box_date.text = ""
        self.text_box_lieu.text = ""
        self.text_box_mot_clef.text = ""
        
        self.type_row = self.drop_down_event.selected_value   
        if self.type_row is None:
            return
            
        # CREATION D'UN NOUVEL EVENEMNT "Nouvel évenemnt"
        if self.type_row['code'] == 0:                        
            from ..Evenements_v2_word_processor import Evenements_v2_word_processor
            open_form('Evenements_v2_word_processor')
            
        # VOIR UN EVENEMNT    
        type_evenement = self.type_row['type']
        self.test_non_valid(type_evenement)  # affiche en rouge le check box erreur de validation 
            
        # Acquisition du check box: Affiche les erreurs de sauvegardes
        visu_des_erreurs = self.check_box_visu_erreurs.checked
        # Création de la liste des évenemnts: NE PRENDRE QUE LES EVENEMNTS SAUVES PAR VALIDATION (sauf si chechk box visu erreurs Checked )
        #   certaines raws viennent de sauvegardes temporaires ttes les 15 sec par forme 'Evenements'
        #      ( venant de sorties incontrolées par fermetures defenêtres ou appuis sur la touche gauche du tel)
        liste = app_tables.events.search(tables.order_by("date", ascending=False),
                                        auto_sov=visu_des_erreurs, 
                                        type_event=type_evenement
                                        )
        self.repeating_panel_1.items=liste
        self.check_box_visu_erreurs.visible = True
        self.data_grid_1.visible = True
        self.column_panel_recherche.visible = True
            
    def check_box_visu_erreurs_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.text_box_date.text = ""
        self.text_box_lieu.text = ""
        self.text_box_mot_clef.text = ""
        self.drop_down_event_change()     


    def text_area_commentaires_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.button_validation.visible = True
        # self.button_validation_1.visible = True
        self.button_validation_2.visible = True

    # validation:   auto_sov True si sovegarde auto tte les 15"   id est l'id
    def button_validation_click(self, auto_sov=False, id=None, **event_args):
        """This method is called when the button is clicked"""
        writing_date_time = (French_zone.french_zone_time())  # now est le jour/h actuelle (datetime object)
        row_lieu = self.drop_down_lieux.selected_value
        lieu_txt = row_lieu["lieu"]
        result, self.id = anvil.server.call(
            "add_event",
            self.id,  # row id   pour réécrire le row en auto sov tt les 15"
            self.drop_down_event.selected_value,  # Type event
            self.date_sov,  # date
            row_lieu,  # lieu row
            lieu_txt,  # lieu en clair
            self.text_area_notes.text,  # notes
            self.image_1.source,  # image 1
            self.image_2.source,
            self.image_3.source,
            writing_date_time,  # Date et heure de l'enregistrement
        )
        if not result:
            alert("Evenement non sauvegardé !")
        # si la sauvegarde a été effectué en fin de saisie de l'évenemnt (clique sur Bt 'Valider')
        if auto_sov is False:
            self.button_annuler_click()

    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:  # pas d'annulation en ouvrant choix de fichier
            nom = self.nom_img(
                "1"
            )  # envoi en fonction d'initialisation du nom de l'image 1
            file_rezized = anvil.server.call(
                "resize_img", file, nom
            )  # 800x600 ou 600x800
            self.image_1.source = file_rezized
            self.button_validation.visible = True

    def file_loader_2_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:  # pas d'annulation en ouvrant choix de fichier
            nom = self.nom_img(
                "2"
            )  # envoi en fonction d'initialisation du nom de l'image 2
            file_rezized = anvil.server.call(
                "resize_img", file, nom
            )  # 800x600 ou 600x800
            self.image_2.source = file_rezized
            self.button_validation.visible = True

    def file_loader_3_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:  # pas d'annulation en ouvrant choix de fichier
            nom = self.nom_img(
                "3"
            )  # envoi en fonction d'initialisation du nom de l'image 3
            file_rezized = anvil.server.call(
                "resize_img", file, nom
            )  # 800x600 ou 600x800
            self.image_3.source = file_rezized
            self.button_validation.visible = True

    def date_picker_1_hide(self, **event_args):
        """This method is called when the DatePicker is removed from the screen"""
        # Change les bt 'apply' en 'Valider'
        from anvil.js.window import document

        for btn in document.querySelectorAll(".daterangepicker .applyBtn"):
            btn.textContent = "Ok"
        for btn in document.querySelectorAll(".daterangepicker .cancelBtn"):
            btn.textContent = "Retour"

    # Pour empêcher le msg session expired (suffit pour ordinateur, pas pour tel)
    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        with anvil.server.no_loading_indicator:
            result = anvil.server.call("ping")
        print("ping on server to prevent 'session expired' every 5 min, server answer:{result}")

    
    # ----------------------------------------------------------------  Recherche sur date
    def text_box_date_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        type_evenement = self.type_row['type']
        
        self.text_box_mot_clef.text = ""
        self.text_box_lieu.text = ""
        c_date = self.text_box_date.text + "%"            #  wildcard search on date
        liste = app_tables.events.search(tables.order_by("date", ascending=False),
                                        date=q.ilike(c_date),
                                        type_event=type_evenement
                                        )
        self.repeating_panel_1.items=liste

    def text_box_date_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.text_box_date_focus()
        
    # ------------------------------------------------------------------  recherche sur mot clef 
    # ERREUR: n'a pas fonctionné car un espace était inséré au début du mot clé (en écriture)
    # avnt l'écriture du row, Il a fallu faire un strip sur le mot clé pour enlever cet espace !!! 
    def text_box_mot_clef_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        type_evenement = self.type_row['type']
        
        self.text_box_date.text = ""
        self.text_box_lieu.text = ""
        
        c_mot_clef = self.text_box_mot_clef.text
        c_mot_clef = c_mot_clef + "%"            #  wildcard search on mot clef
        liste = app_tables.events.search(tables.order_by("mot_clef", ascending=True),
                                        mot_clef=q.ilike(c_mot_clef),
                                        type_event=type_evenement
                                        )
        self.repeating_panel_1.items=liste
    
    def text_box_mot_clef_change(self, **event_args):
       self.text_box_mot_clef_focus()

    
    # ------------------------------------------------------------------  recherche sur lieu
    def text_box_lieu_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        type_evenement = self.type_row['type']
            
        self.text_box_date.text = ""
        self.text_box_mot_clef.text = ""
        
        c_lieu = self.text_box_lieu.text + "%"            #  wildcard search on date
        liste = app_tables.events.search(tables.order_by("lieu", ascending=True),
                                        lieu_text=q.ilike(c_lieu),
                                        type_event=type_evenement
                                        )
        self.repeating_panel_1.items=liste
    
    def text_box_lieu_change(self, **event_args):
        """This method is ca c_nom = self.text_box_nom.text + "%"            #         nomlled when the TextBox gets focus"""
        self.text_box_lieu_focus()


    # Affiche en rouge self.check_box_visu_erreurs si un ou plusieurs rows sont non validées
    def test_non_valid(self, type_evenement):
        liste_rows_non_valide = app_tables.events.search(
                                                        auto_sov=True, 
                                                        type_event=type_evenement
                                                        )
        if len(liste_rows_non_valide)>0:
            self.check_box_visu_erreurs.background = "theme:Error"



 
   

 



 


