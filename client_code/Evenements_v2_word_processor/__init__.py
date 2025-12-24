from ._anvil_designer import Evenements_v2_word_processorTemplate
from anvil import *
import anvil.users
import anvil.server

import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import French_zone  # pour afficher la date du jour
from datetime import datetime
from ..Word_editor import Word_editor   # Word processor component inséré ds self.content_panel
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML

# Change les bt 'apply' en 'Valider' si je veux saisir l'heure en même tps que la date (picktime set à True)
# VOIR DATE PICKER, SHOW EVENT

# Saisie d'un évenement ou d'un incident ou entretien ind.
#   Pb rencontré: session expired si la saisie est intérrompue
# 2 Solutions implémentées:  - Un 'ping' sur le serveur toutes les 5 minutes (300" timer 1) empêche la session d'expirer (sur un ordinateur)
#                                mais pas sur un tel qd l'écran s'étteint....
#                            - Une sauvegarde auto toutes les 1 secondes (timer 2), ce qui permet de ne pas perdre bp de données si expired.


class Evenements_v2_word_processor(Evenements_v2_word_processorTemplate):
    def __init__(self, to_be_modified_row=None, origine="", **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()
        # origine n'est pas vide si cette forme a été appelée en modification (click sur une row en Evenements_visu_modif_del)
        #    permet de tester l'origine si BT annuler est cliqué
        self.origine = (origine)  # origine = "modif" si viens de Evenements_visu_modif_del

        # Drop down codes lieux
        self.drop_down_lieux.items = [(r["lieu"], r) for r in app_tables.lieux.search(tables.order_by("lieu", ascending=True))]
        # for lieu in self.drop_down_lieux.items:
        # print(lieu, lieu[0], lieu[1])
        liste = self.drop_down_lieux.items[0]
        self.drop_down_lieux.selected_value = liste[1]

        # Drop down codes type évenements
        liste_event = []
        for r in app_tables.event_types.search(tables.order_by("code", ascending=True)):
            if (r["code"] != 0):  # on ne prend pas le code 0 qui est le row "nouvel évenement"
                liste_event.append((r["msg_0"], r))  # on ajoute le msg "nouvel ..."
        self.drop_down_event.items = liste_event
        # for type in self.drop_down_event.items:
        # print(type, type[0], type[1])

        self.now = (French_zone.french_zone_time())  # now est le jour/h actuelle (datetime object)
        self.date_sov = self.now.strftime("%Y_%m_%d %H_%M")  # exraction de la AAAA_MM_JJ hh_mm pour nom fichier image

        # Test si ouverture en mode Création ou modif (self.to_be_modified_row = None si création)  Initialisé en init
        self.to_be_modified_row = to_be_modified_row
        if self.to_be_modified_row is None:             # Creation d'un évenement
            
            self.mode = "creation"
            self.id = None
            self.text_area_mot_clef.text = ""
            self.outlined_card_main.visible = False

            self.image_1.source = None
            self.outlined_card_1.visible = False

            self.image_2.source = None
            self.outlined_card_2.visible = False

            self.image_3.source = None
            self.outlined_card_3.visible = False

            # Init drop down date avec Date du jour et acquisition de l'heure
            t = str(self.now)
            # Extraire l'année, le mois et le jour à partir de la chaîne
            yy = t[0:4]  # 0 à 4, 4 non inclus
            mm = t[5:7]
            dd = t[8:10]
            hh = t[11:13]
            mi = t[14:16]
            # Création de la variable de type date
            self.date1 = datetime(int(yy), int(mm), int(dd), int(hh), int(mi))  # réutilisée pour le nom des images
            self.date_picker_1.pick_time = True
            self.date_picker_1.date = self.date1
        else:                                                                                            # MODIF d'un évenement
            # Modif à partir du row passé en init par la form Evenements_visu_modif_del
            self.mode = "modif"
            # Test si ce row n'avait pas été validé
            #if self.to_be_modified_row["auto_sov"] is True:
            #    alert("Saisie Evenement non achevée normalement.\n Vous pouvez maintenant achever sa saisie ou le valider directement.")
                #self.button_validation.visible = True

            self.id = self.to_be_modified_row.get_id()
            self.drop_down_event.visible = False
            # initilisation des composants de cette forme par le row passé en init par la form Evenements_visu_modif_del

            #   0123456789
            # t=2023/01/17
            t = self.to_be_modified_row["date"]
            # Extraire l'année, le mois et le jour à partir de la chaîne
            yy = t[0:4]  # 0 à 4, 4 non inclus
            mm = t[5:7]
            dd = t[8:10]
            hh = t[11:13]
            min = t[14:16]
            # Création de la variable de type date
            self.date1 = datetime(int(yy), int(mm), int(dd), int(hh), int(min))
            self.date_picker_1.pick_time = True
            self.date_picker_1.date = self.date1

            type_evenement = self.to_be_modified_row["type_event"]
            self.drop_down_event.selected_value = type_evenement

            self.drop_down_lieux.selected_value = self.to_be_modified_row["lieu"]
            self.text_area_mot_clef.text = self.to_be_modified_row["mot_clef"]
            self.text_area_notes.text = self.to_be_modified_row["note"]

            texte_brut = self.to_be_modified_row["note"]
            paragraphs = texte_brut.split("\n\n")

            # module pour ajouter les sauts de pages en modif 
            html_list = []
            for p in paragraphs:
                p2 = p.replace("\n", "<br>")  # en HTML \n non reconnu, remplacé par <br>
                html_list.append(f"<p>{p2}</p>")
            html_text = "".join(html_list)

            self.call_word_editor(html_text) # Appel du Word Editor par fonction utilisé aussi pour la création d'un event
           

            if self.to_be_modified_row["img1"] is not None:
                self.image_1.source = self.to_be_modified_row["img1"]
                self.column_panel_trav_sur_img_1.visible = True
                self.flow_panel_loader_1.visible = False
            else:
                self.image_1.source = None
                self.outlined_card_1.visible = False
                self.flow_panel_loader_1.visible = True

            if self.to_be_modified_row["img2"] is not None:
                self.image_2.source = self.to_be_modified_row["img2"]
                self.column_panel_trav_sur_img_2.visible = True
                self.flow_panel_loader_2.visible = False
            else:
                self.image_2.source = None
                self.outlined_card_2.visible = False
                self.flow_panel_loader_2.visible = True

            if self.to_be_modified_row["img3"] is not None:
                self.image_3.source = self.to_be_modified_row["img3"]
                self.column_panel_trav_sur_img_3.visible = True
                self.flow_panel_loader_3.visible = False
            else:
                self.image_3.source = None
                self.outlined_card_3.visible = False
                self.flow_panel_loader_3.visible = True

            self.flow_panel_lieu_date.visible = True
            self.outlined_card_main.visible = True

        # Init drop down event (Pour l'instant choix à rentrer pour ne pas perdre les notes si je change le type d'evenmt)
        """
        self.drop_down_event.selected_value = self.drop_down_event.items[0]  # "Réunion"
        self.note_for_meeting("meeting")
        """

    def drop_down_event_change(self, **event_args):
        """This method is called when an item is selected"""
        # self.drop_down_event.selected_value = self.drop_down_event.items[0]  # "Réunion"
        self.type_row = self.drop_down_event.selected_value  # row du type d'évenemnts
        self.flow_panel_lieu_date.visible = True
        self.outlined_card_main.visible = True
        heure = self.now.time()
        heure = heure.strftime("%H:%M")
        date0 = self.now.date()
        date = date0.strftime("%d/%m/%Y")
        
        self.text_area_notes.text = self.type_row["text_initial"]  # col text_initial table Event_types
        
        self.text_area_mot_clef.text = ""
        if self.type_row["mot_clef_setup"] is True:
            self.text_area_mot_clef.text = f"Réunion du {date}"
        else:
            self.text_area_mot_clef.text = self.type_row['type'].capitalize()
        self.call_word_editor(self.type_row["text_initial"]) # Appel du Word Editor avec texte initial (fonction utilisée aussi pour 'modif')

    """
    =============================================================================================================================================      CALL FOR THE WORD EDITOR
    """
    def call_word_editor(self, content_text_html):
        evnt = self.drop_down_event.selected_value  # (réunion, incident ...)
        self.flow_panel_drop_type_evnt.visible = False  # cache le drop down type d'evnt
        title = f"Notes prises sur un évenement: {evnt} du {self.date_picker_1.date.strftime('%d/%m/%Y')}"
        sub_title = f"Mot clé: {self.text_area_mot_clef.text}"
        # INSERTION TEXT-EDITOR form 'Word_editor'  (voir import)
        text_editor = Word_editor()  # title/sub_title : pour le bt download 
        text_editor.text = content_text_html   # .text: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        text_editor.top_ligne_1 = title              # pdf title when download 
        text_editor.top_ligne_2 = sub_title          # pdf sub_title when download 
        
        if self.origine == "modif":
            text_editor.param1 = "modif"
        else:
            text_editor.param1 = "creation"
        #text_editor.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        
        # y a til eu un changement dans le texte ? si oui affiche le bt validation
        text_editor.set_event_handler("x-text-changed-state", self._on_text_changed_state)
        
        # attendre que la forme fille soit pr^te pour gérer le bt_validation
        self._editor_ready = False
        text_editor.set_event_handler("x-editor-ready", self._arm_editor_ready)
        
        # récup du text chaque seconde, repris lors de la validation
        text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 1 sec, timer_2 de la form Word_editor
        self.content_panel.add_component(text_editor)
    """
    =================================================================================================================================================================================
    # Réaction aux modifications du texte : on affiche le bt Validation
    # ------------------------------------------------------------------
    """
    def _on_text_changed_state(self, sender, **e):
        if not self._editor_ready:
            return  # on ignore les events de chargement
        self.button_validation.visible = True   
        self.mode = sender.param1   # création / modif
        self.texte_a_sauver = sender.text

    # handler por afficher le bouton validation uniqt qd text est modifié
    # ! self._editor_ready = False en création de la forme
    def _arm_editor_ready(self, **e):
        self._editor_ready = True    

    # Event raised every 1 sec: Automatic backup of the text in Word_editor form
    def timer_text_backup(self, sender, **event_args):
        """This method is called Every 15 seconds. Does not trigger if [interval] is 0."""
        # Toutes les 15 secondes, sauvegarde auto, self.id contient l'id du row qui est en cours de saisie
        with anvil.server.no_loading_indicator:
            self.validation(True, self.id, sender.text)  # auto sov: TRUE

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.validation(False, self.id, self.texte_a_sauver)  # auto sov: TRUE
    
    def text_area_commentaires_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        #self.button_validation.visible = True
        # self.button_validation_1.visible = True
    

    # validation:   auto_sov True si sauvegarde auto tte les 1", appelé par timer_2_tick
    def validation(self, auto_sov=False, id=None, html_text="", **event_args):
        """This method is called when the button is clicked"""
        if self.mode == "creation":
            type_row = self.drop_down_event.selected_value
            type_evenement = type_row["type"]  # reunion/entretien/incident ...

        if self.mode == "modif":
            type_evenement = self.to_be_modified_row["type_event"]

        row = app_tables.event_types.get(type=type_evenement)

        
        # Vraie validation, test si mot clef vide
        if (len(self.text_area_mot_clef.text) == 0 and auto_sov is False):  
            mk_temp = row['type']
            msg = f"Le mot clef temporaire '{mk_temp}' a été créé car il était vide"
            AlertHTML.info("Oublie :",msg)
            self.text_area_mot_clef.text = mk_temp

        # Il y aura une recherche spéciale (#  wildcard search) sur le 'mot_clef' en Evenements_visu_modif_del
        # enlève les espaces à gauche et droite, sinon, erreur en recherche
        mot_k = self.text_area_mot_clef.text
        mot_k = mot_k.strip()
  
        writing_date_time = (French_zone.french_zone_time())  # now est le jour/h actuelle (datetime object)
        row_lieu = self.drop_down_lieux.selected_value
        lieu_txt = row_lieu["lieu"]

        date_sov = str(self.date_picker_1.date)
        date_sov = date_sov[0:16]
        date_sov = date_sov.replace("-", " ")
        result, self.id = anvil.server.call(
            "add_event",
            self.id,  # row id   pour réécrire le row en auto sov tt les 15"
            auto_sov,  # False si bt validation utilisé   /   True si sauvegarde auto lancée par timer2, ts les 15 secondes
            type_evenement,  # Type event: réunion, incident, entretien
            row,  # link avec table event_types
            date_sov,  # date
            row_lieu,  # lieu row
            lieu_txt,  # lieu en clair
            #self.text_area_notes.text,  # --------------- notes
            html_text,  # ----------------------------------------------------- notes HTML
            self.image_1.source,  # image 1
            self.image_2.source,
            self.image_3.source,
            writing_date_time,  # Date et heure de l'enregistrement
            mot_k,  # Mot clef pour accès rapide en recherche
        )
        if result is not True:
            AlertHTML.error("Erreur :", f"Evenement non sauvegardé ! <br><br>{result}")

        # si la sauvegarde a été effectuée en fin de saisie de l'évenemnt (clique sur Bt 'Valider'), on sort en renvoyant le type d'évenemnt pour initiliser la drop down
        if auto_sov is False:
            # sortie normale
            # renvoyer le type d'évenemnt actuel: row event_types
            from ..Evenements_visu_modif_del import Evenements_visu_modif_del
            open_form("Evenements_visu_modif_del", row)

    # Une sauvegarde a déjà été effectuée, j'efface cette sauvegarde temporaire SI JE VIENS DE CREER CET EVNT (origine="")
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.id is not None and self.origine == "":
            result = anvil.server.call("del_event_bt_retour", self.id)
            if not result:
                alert("Sauvegarde temporaire non effacée !")
        open_form("Evenements_visu_modif_del")

    # Image1 en chargement
    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:  # pas d'annulation en ouvrant choix de fichier
            nom = self.nom_img(
                "1"
            )  # envoi en fonction d'initialisation du nom de l'image 1
            file_resized = anvil.server.call(
                "resize_img", file, nom
            )  # 800x600 ou 600x800
            self.image_1.source = file_resized
            self.file_loader_1.text = "1 img chargée"
            #self.button_validation.visible = True

            self.flow_panel_loader_1.visible = False
            self.outlined_card_1.visible = True
            self.button_rotation_1.visible = True
            self.button_del_1.visible = True
            self.button_visu_1.visible = True

    def file_loader_2_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:  # pas d'annulation en ouvrant choix de fichier
            nom = self.nom_img(
                "2"
            )  # envoi en fonction d'initialisation du nom de l'image 2
            file_resized = anvil.server.call(
                "resize_img", file, nom
            )  # 800x600 ou 600x800
            self.image_2.source = file_resized
            self.file_loader_2.text = "1 img chargée"
            #self.button_validation.visible = True

            self.flow_panel_loader_2.visible = False
            self.outlined_card_2.visible = True
            self.button_rotation_2.visible = True
            self.button_del_2.visible = True
            self.button_visu_2.visible = True

    def file_loader_3_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:  # pas d'annulation en ouvrant choix de fichier
            nom = self.nom_img(
                "3"
            )  # envoi en fonction d'initialisation du nom de l'image 3
            file_resized = anvil.server.call(
                "resize_img", file, nom
            )  # 800x600 ou 600x800
            self.image_3.source = file_resized
            self.file_loader_3.text = "1 img chargée"
            #self.button_validation.visible = True

            self.flow_panel_loader_3.visible = False
            self.outlined_card_3.visible = True
            self.button_rotation_3.visible = True
            self.button_del_3.visible = True
            self.button_visu_3.visible = True

    # POur afficher OK et Retour en FRancais (calendrier)
    # Cette méthode se lance qd le date_picker component s'affiche
    def date_picker_1_show(self, **event_args):
        # Change les bt 'apply' en 'Valider'
        from anvil.js.window import document

        for btn in document.querySelectorAll(".daterangepicker .applyBtn"):
            btn.textContent = "Ok"
        for btn in document.querySelectorAll(".daterangepicker .cancelBtn"):
            btn.textContent = "Retour"

    
    # Initialisation du préfixe du nom du fichier img
    def nom_img(self, num_img_txt):
        date = str(self.date1)[0:16]
        date = date.replace(" ", "-")
        nom_img = "Evenement " + num_img_txt + " du " + date
        return nom_img

    def button_visu_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Pre_Visu_img import Pre_Visu_img

        open_form("Pre_Visu_img", self.image_1.source)

    def button_rotation_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        file = self.image_1.source
        self.image_1.source = anvil.image.rotate(file, 90)
        #self.button_validation.visible = True

    def button_del_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.image_1.source = None
        #self.button_validation.visible = True
        self.outlined_card_1.visible = False
        self.flow_panel_loader_1.visible = True
        self.file_loader_1.text = "Photo1"

    def button_visu_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Pre_Visu_img import Pre_Visu_img
        open_form("Pre_Visu_img", self.image_2.source)

    def button_rotation_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        file = self.image_2.source
        self.image_2.source = anvil.image.rotate(file, 90)
        #self.button_validation.visible = True

    def button_del_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.image_2.source = None
        #self.button_validation.visible = True
        self.outlined_card_2.visible = False
        self.flow_panel_loader_2.visible = True
        self.file_loader_2.text = "Photo2"

    def button_visu_3_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Pre_Visu_img import Pre_Visu_img
        open_form("Pre_Visu_img", self.image_3.source)

    def button_rotation_3_click(self, **event_args):
        """This method is called when the button is clicked"""
        file = self.image_3.source
        self.image_3.source = anvil.image.rotate(file, 90)
        #self.button_validation.visible = True

    def button_del_3_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.image_3.source = None
        #self.button_validation.visible = True
        self.outlined_card_3.visible = False
        self.flow_panel_loader_3.visible = True
        self.file_loader_3.text = "Photo3"

    def drop_down_lieux_change(self, **event_args):
        """This method is called when an item is selected"""
        #self.button_validation.visible = True

    def date_picker_1_change(self, **event_args):
        """This method is called when the selected date changes"""
        #self.button_validation.visible = True

    # =================================================================================================  RAISED EVENTS TREATMENTS
    

            
   
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form
    def handle_click_fin_saisie(self, sender, **event_args):
        # sender.text contains the 'Word_editor'form's HTML text
        #print(sender.text)
        self.validation(False, self.id, sender.text)

    def button_visu_html_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.text_area_notes.visible is False:
            self.text_area_notes.visible = True
        else:
            self.text_area_notes.visible = False

    

   
   