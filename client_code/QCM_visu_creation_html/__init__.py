from ._anvil_designer import QCM_visu_creation_htmlTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js import window
import time
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML

class QCM_visu_creation_html(QCM_visu_creation_htmlTemplate):
    def __init__(self, qcm_row, nb_questions=0, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        """-------------------------------------------------------------------------------------------
        GESTION en INIT du VIDEO PLAYER
        """
        # 0 - Initialisation del'url à None pour sauver en table
        self.url_video = None
        # 1 - Initilisation du component de cette form Video_player_1
        self.init_video_player()  # appel fonction dans cette forme
        
        # 2 - initialisation liste des videos pour drop_down_videos_list
        """
        list_videos = None
        list_videos = app_tables.files.search()
        if list_videos is not None:
            self.drop_down_videos_list.items = [
                (r["path"], r) for r in app_tables.files.search(tables.order_by("path", ascending=True)
                                                                                                      )
                                                ]
        # test avec la video de test en assets   
        self.drop_down_videos_list.items = ["https://amsdata-v2.anvil.app/_/theme/Videos_test/Essai1_stream.mp4"]  
        self.drop_down_videos_list.visible = True
        """
        # Pi5 est OK, ce sera la même logique mais alimentée en uplink par scan du répertoire Pi5 avec:
        
        #----- Init du drop down des videos dispo en Pi5
        list_videos = anvil.server.call("get_video_urls")
        for v in list_videos:
            print(v["name"], v["url"])
            
        self.drop_down_videos_list.items = [
            (v["name"], v["url"]) for v in list_videos
        ]
               
        """---------------------------------------------------------------------------------------------
        FIN GESTION en Init du VIDEO PLAYER
        """
        
        self.first_correction = True  # indiquera si 1ere press on bt correction
        self.qcm_row = qcm_row  # QCM descro row
        self.label_nb_questions.text = nb_questions + 1
        self.num_question.text = nb_questions + 1   # Num ligne à partir du nb lignes déjà créées
        self.type_question = ""
        self.image_1.source = None

        self.rep1.visible = False
        self.rep2.visible = False
        self.rep3.visible = False
        self.rep4.visible = False
        self.rep5.visible = False
        # réponses
        self.rep1.checked = False
        self.rep2.checked = False
        self.rep3.checked = False
        self.rep4.checked = False
        self.rep5.checked = False

        self.rich_text_question.content = ""
        self.rich_text_correction.content = "Correct°"
        self.button_question.visible = False
        # Initialisation des drop down nb potions et Barême
        self.drop_down_nb_options.items=([("Vrai/Faux", 1), ("2 options", 2), ("3 options", 3), ("4 options", 4), ("5 options", 5)])

        self.drop_down_bareme.visible = False
        self.drop_down_bareme.items = ["1", "2", "3", "4", "5", "10"]
        self.drop_down_bareme.selected_value = "1"
        
        #self.drop_down_bareme.selected_value = None
        # =========================================================================================
        # POUR AUTO SAUVEGARDE DU TEXTE:
        # Bouton Validation caché tant que rien n'est modifié
        self.button_validation.visible = False
        self._editor_ready = False
        # pour vérifier si il y a eu une modif du texte
        self._last_saved_text = ""
        # 1- Écoute l'état de modification du Word Editor
        self.word_editor_1.set_event_handler("x-text-changed-state", self._on_text_changed_state)

        # 2- handler sur l'INSTANCE word_editor_1  raised each sec to get the updated text
        self.word_editor_1.set_event_handler("x-timer_text_backup", self._backup_word_editor)
        # =========================================================================================
        # pour afficher le bt validation uniqt qd le texte est modifié en INSTANCE word_editor_1
        self.word_editor_1.set_event_handler("x-editor-ready", self._arm_editor_ready)

        # on affiche la correction en init, la question est ds le word editor
        self.rich_text_correction.content = "Correction"
        self.rich_text_correction.visible = True  # display the Correction Rich Text

        self.rich_text_question.content = ""
        self.rich_text_question.visible = False
        
    """---------------------------------------------------------------------------------------------------------------------------
    Fonctions de GESTION du VIDEO PLAYER
    """

    # appelé en init
    def init_video_player(self):
        self.video_player_1.clear()
        self.video_player_1.visible = False

    # handler change sur drop_down_videos_list
    def drop_down_videos_list_change(self, **event_args):
        """This method is called when an item is selected"""
        media_url = self.drop_down_videos_list.selected_value  # ici c'est la row 'files'
        print(media_url)
        if not media_url:
            self.video_player_1.clear()
            self.video_player_1.visible = False
            return

        self.column_panel_img.visible = False
        #media = video_row['file']  # récupère la colonne Media appelée file (si video en assets)
        media_url = self.drop_down_videos_list.selected_value  # récupère la colonne Media appelée file
        if media_url:
            print(f"URL de la vidéo choisie: {media_url}")
            self.video_player_1.visible = True
            # si test avec video en asset appeler : self.video_player_1.load_media(
            self.video_player_1.load(
                media_url,
                autoplay=False,
                muted=False,
                controls=True,
                allow_download=True
            )
            # affiche le cp video
            self.column_panel_video_player.visible = True
            # pour sauver l'url en table 
            self.url_video = media_url           # ----------------------------------- video url Sauvée en table qcm 
            return
        
        # Sinon : rien d’utilisable
        self.video_player_1.clear()
        self.video_player_1.visible = False

        self.button_modif_color()
    """-------------------------------------------------------------------------------------------
    Fin des Fonctions de GESTION du VIDEO PLAYER
    """

    
    # appelé par l'init de cette forme ET l'event du Word_Editor module / timer2
    def _backup_word_editor(self, **e):
        html = e.get("text")
        if not html:
            return

        # --- 1) rien n'a changé ---
        if html == self._last_saved_text:
            return

        self.word_editor_1.text = html
        self.button_validation.visible = True

    # ------------------------------------------------------------------
    # Réaction aux modifications du texte : on affiche le bt Validation
    # ------------------------------------------------------------------
    def _on_text_changed_state(self, **e):
        if not self._editor_ready:
            return  # on ignore les events de chargement

            self.button_modif_color()  #affiche bt valid

    def button_modif_color(self):
        self.button_validation.visible = True

    def button_question_click(self, **event_args):
        """This method is called when the button is clicked"""

        self.button_validation.visible = False
        self.rich_text_correction.visible = True  # Hiding the Correction text
        self.rich_text_question.visible = False
        self.button_question.visible = False
        self.button_correction.visible = True
        text_not_html = self.rich_text_question.content
        self.sending_to_word_editor(text_not_html, "question")
        
        
    def button_correction_click(self, **event_args):
        """This method is called when the button is clicked"""

        # Au moins une réponse de Vrai
        if self.rep1.checked is False and \
            self.rep2.checked is False and \
            self.rep3.checked is False and \
            self.rep4.checked is False and \
            self.rep5.checked is False :
            alert("Entrez les Réponses !")
            return
            
        if self.first_correction is True:
            # 1ere entrée en correction, je préforme la correction en fonction des réponses
            texte_de_base = (
                "<span id='qcm-editable' "
                "style='display:block;color:rgb(0,192,250);font-weight:bold;'>"
                "Correction: "
                "</span>"
            )
            if self.choix == 1: # V/F
                if self.rep1.checked is True:
                    texte_correction = "<ul><li>A Vrai :&nbsp&nbsp;</li><li>B Faux :&nbsp&nbsp;</li></ul>"
                else:
                    texte_correction = "<ul><li>A Faux :&nbsp&nbsp;</li><li>B Vrai :&nbsp&nbsp;</li></ul>"
                    
            if self.choix > 1: # V/F
                texte_correction = (
                    "<ul style='margin:0;padding-left:24px;list-style-position:inside;"
                    "color:#fff905;'>"
                )
                
                # A
                texte_correction += f"<li>A {'Vrai ' if self.rep1.checked else 'Faux '} :&nbsp </li>"
                
                # B
                if self.choix > 1:
                    texte_correction += f"<li>B {'Vrai ' if self.rep2.checked else 'Faux '} :&nbsp </li>"
                
                # C
                if self.choix > 2:
                    texte_correction += f"<li>C {'Vrai ' if self.rep3.checked else 'Faux '} :&nbsp </li>"
                
                # D
                if self.choix > 3:
                    texte_correction += f"<li>D {'Vrai ' if self.rep4.checked else 'Faux '} :&nbsp </li>"
                
                # E
                if self.choix > 4:
                    texte_correction += f"<li>E {'Vrai ' if self.rep5.checked else 'Faux '} :&nbsp </li>"
                
                texte_correction += "</ul>"
                
            texte_correction_final = texte_de_base + texte_correction
            
        self.button_validation.visible = False
        self.rich_text_correction.visible = False  # hidding the Correction text
        self.rich_text_question.visible = True
        self.button_question.visible = True
        self.button_correction.visible = False
        self.rich_text_question.content = self.word_editor_1.text 
        
        if self.first_correction is False: # pas le 1er click sur le bt correction 
            text_not_html = self.rich_text_correction.content
            self.sending_to_word_editor(text_not_html, "correction")
        else: # 1er click
            self.sending_to_word_editor(texte_correction_final, "correction")
        self.first_correction = False   # entrée pour la première fois effectuée
        
    def sending_to_word_editor(self, text_not_html, type_text, **event_args):
        # ajout des sauts de ligne HTML (les anciens questions en table peuvent encore contenir \n au lieu de <br>)
        paragraphs = text_not_html.split("\n\n")
        html_list = []
        for p in paragraphs:
            p2 = p.replace("\n", "<br>")  # en HTML \n non reconnu, remplacé par <br>
            html_list.append(f"<p>{p2}</p>")
        html_text = "".join(html_list)
        # -----------------------------------------------------------------------
        # Word_Editor buttons parameters: (through form 'Word_Editor' proprieties)
        self.word_editor_1.bt_exit_visible = False
        if window.innerWidth > 800:
            self.word_editor_1.bt_valid_text = "Validation de la Question"
            self.word_editor_1.bt_exit_text = "Sortie"
        elif window.innerWidth < 450:
            self.word_editor_1.bt_valid_text = ""
            self.word_editor_1.bt_exit_text = ""
        else:
            self.word_editor_1.bt_valid_text = "Validat°"
            self.word_editor_1.bt_exit_text = "Sortie"
        # Word_Editor PDF download titles parameters:
        self.word_editor_1.top_ligne_2 = "Nouvelle Question"
        self.top_ligne_2 = self.top_ligne_1 = f"QCM {self.qcm_row['destination']} "

        # Text to be modified by Word_Editor
        self.word_editor_1.remove_on_exit = False
        self.word_editor_1.param1 = type_text  # 'question' or 'correction'
        self.word_editor_1.param2 = 'creation'  # 'question' or 'correction'
        self.word_editor_1.text = html_text
        self.word_editor_1.form_show()  # will execute the show event in Word_Editor form
        self.word_editor_1.visible = True  # 'Word_Editor' component display

        if self.word_editor_1.param1 == "question":
            self.rich_text_correction.visible = True  # display the Correction Rich Text
            self.rich_text_question.visible = False  # display the Question Rich Text
            self.rich_text_question.content = html_text

        if self.word_editor_1.param1 == "correction":
            self.rich_text_correction.visible = False  # display the Correction Rich Text
            self.rich_text_question.visible = True  # display the Question Rich Text
            self.rich_text_correction.content = html_text

    # handler pour afficher le bouton validation uniqt qd text est modifié
    def _arm_editor_ready(self, **e):
        self._editor_ready = True

    # Button validation, auto=True qd sauv auto du timer2 de Word_Editor (voir l'init de cette forme)
    def button_validation_click(self, sov_auto=False, **event_args):  # =============  VALIDATION
        """This method is called when the button is clicked"""
        
        # type de question 
        if self.drop_down_nb_options.selected_value == 1:    # type V/F 
            type = "V/F"       # rep1 ou rep2 peuvent être vrai
        else:
            type = "Multi"     # rep1 et rep2 peuvent être vrai 

        # param (descro du QCM)
        param = self.qcm_row ["destination"]
        mode = self.word_editor_1.param1  # mode 'question' / "correction"
        html = self.word_editor_1.text   # le text édité
        
        if mode == "question":
            # Affichage
            self.rich_text_correction.visible = True
            self.rich_text_question.visible = False
            self.rich_text_question.content = html  # affichage seulement
        
            # Sauvegarde : on prend la source propre
            question = html
            correction = self.rich_text_correction.content  # l'autre champ (pas modifié ici)
        
        elif mode == "correction":
            # Affichage
            self.rich_text_correction.visible = False
            self.rich_text_question.visible = True
            self.rich_text_correction.content = html  # affichage seulement
        
            # Sauvegarde : on prend la source propre
            correction = html
            question = self.rich_text_question.content  # l'autre champ (pas modifié ici)
        
        if self.drop_down_nb_options.selected_value is None:
            alert("Choisissez un type de question !")
            return
        if self.drop_down_bareme.selected_value is None:
            alert("Choisissez un barême !")
            return
            
        rep_multi_stagiaire = ""  # CUMUL de la codif des réponses du stagiaire
        if self.choix == 1: #V/F":
            if self.rep1.checked is True:  # question V/F
                rep_multi_stagiaire = "10"
            else:
                if self.rep2.checked is True:  # question V/F
                    rep_multi_stagiaire = "01"
                else:
                    alert("Choisissez une réponse V/F !")
                    return
        else:
            if self.rep1.checked is True:  # question non V/F
                rep_multi_stagiaire = "1"
            else:
                rep_multi_stagiaire = "0"

            if self.choix > 1:
                if self.rep2.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"
                if rep_multi_stagiaire == "00":
                    alert("Choisissez une réponse !")
                    return

            if self.choix > 2:
                if self.rep3.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"
                if rep_multi_stagiaire == "000":
                    alert("Choisissez une réponse !")
                    return
                    
            if self.choix > 3:
                if self.rep4.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"
                if rep_multi_stagiaire == "0000":
                    alert("Choisissez une réponse !")
                    return

            if self.choix > 4:
                if self.rep5.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"
                if rep_multi_stagiaire == "00000":
                    alert("Choisissez une réponse !")
                    return
                    
        if len(self.rich_text_correction.content) < 14:
            r = AlertConfirmHTML.ask(
                "La correction est vide !",
                "<p>Voulez-vous vraiment quitter ?</p>",
                style="info",
                large = True
            )
            if not r :   # non 
                return
             
        result = anvil.server.call("add_ligne_qcm",
            int(self.num_question.text),  # num question (numériqie)
            question,                     # question HTML
            correction,                   # correction HTML               
            rep_multi_stagiaire,          # rep codée ex 10 /  010 ...
            self.drop_down_bareme.selected_value,  # Bareme de la question
            self.image_1.source,  # photo
            self.qcm_row,         # qcm descro row                  
            type,                 # "V/F" ou "Multi"
            param,                 # self.qcm_row ["destination"], description du QCM
            self.url_video              # text: url de la vidéo (None si pas de video)         
        )
        
        if result:
            n = Notification("Création de la question !",
                             timeout=1)   # par défaut 2 secondes
            n.show()
            # raffraichit les lignes qcm en récupérant le choix du qcm ds la dropdown
            from anvil import open_form       # j'initialise la forme principale avec le choix du qcm ds la dropdown
            open_form("QCM_visu_modif_Main", self.qcm_row)
        else:
            alert("erreur de création d'une question QCM")
 
    def button_retour_click(self, **event_args):  # =============  RETOUR
        """This method is called when the button is clicked"""
        qcm_descro_nb = self.qcm_row
        open_form("QCM_visu_modif_Main", qcm_descro_nb)
    

    # ------------------------------------------------------------------
    # Chargement initial du contenu
    # ------------------------------------------------------------------
    def load_qcm_content(self, html):
        self.word_editor_1.set_initial_html(html)


    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        thumb_pic = anvil.image.generate_thumbnail(file, 640)
        self.image_1.source = thumb_pic
        self.column_panel_video.visible = False
        self.column_panel_image.visible = True
        self.button_modif_color()

    def drop_down_nb_options_change(self, **event_args):
        """This method is called when an item is selected"""
        self.drop_down_bareme.visible = True
        
        self.rep1.visible = True
        self.rep2.visible = True
        self.rep3.visible = True
        self.rep4.visible = True
        self.rep5.visible = True
        
        self.rep1.checked = False
        self.rep2.checked = False
        self.rep3.checked = False
        self.rep4.checked = False
        self.rep5.checked = False
        self.choix = self.drop_down_nb_options.selected_value
        #print(self.choix, type(self.choix))
        #texte_de_base="<span style='display:block;color:rgb(0,192,250);font-weight:bold;'>Question&nbsp;:&nbsp;</span>"
        # 
        texte_de_base = (
            "<span id='qcm-editable' "
                "style='display:block;color:rgb(0,192,250);font-weight:bold;'>"
                "Saisissez la question ici"
            "</span>"
        )
        
        texte_complet = ""
        
        if self.choix == 1:   # Vrai/ Faux    l'1 ou l'autre, rep1 et rep2 ne peuvent pas  être identiques
            self.rich_text_question.content = texte_de_base
            self.rep3.visible = False
            self.rep4.visible = False
            self.rep5.visible = False
            self.rep1.text = "Vrai"
            self.rep2.text = "Faux"
            texte_complet = texte_de_base

        if self.choix > 1:     # 2 options possibles, rep1 et rep2 peuvent être identiques  ex 11 
            self.rep1.text = "A"
            self.rep2.text = "B"
            self.rep3.visible = False
            self.rep4.visible = False
            self.rep5.visible = False
            bloc_add = "<ul><li>A&nbsp&nbsp;</li><li>B&nbsp&nbsp;</li></ul>"
            texte_complet = texte_de_base + bloc_add
            
        if self.choix > 2:     # au moins 3 options possibles, rep1 à rep3 peuvent être identiques  ex 111
            self.rep3.visible = True
            self.rep4.visible = False
            self.rep5.visible = False
            bloc_add = "<ul><li>A&nbsp&nbsp;</li><li>B&nbsp&nbsp;</li><li>C&nbsp&nbsp;</li></ul>"
            texte_complet = texte_de_base + bloc_add
            
        if self.choix > 3:     # au moins 4 options possibles, rep1 et rep4 peuvent être identiques  ex  1111
            self.rep4.visible = True
            self.rep5.visible = False
            bloc_add = "<ul><li>A&nbsp&nbsp;</li><li>B&nbsp&nbsp;</li><li>C&nbsp&nbsp;</li><li>D&nbsp&nbsp;</li></ul>"
            texte_complet = texte_de_base + bloc_add
            
        if self.choix > 4:     # 5 options possibles, rep1 à rep2 peuvent être identiques
            self.rep5.visible = True
            bloc_add = "<ul><li>A&nbsp&nbsp;</li><li>B&nbsp&nbsp;</li><li>C&nbsp&nbsp;</li><li>D&nbsp&nbsp;</li><li>E&nbsp&nbsp;</li></ul>"
            texte_complet = texte_de_base + bloc_add

        # -----------------------------------------------------------------------
        self.sending_to_word_editor(texte_complet, "question")
        self.button_modif_color()

    def rep1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.choix == 1: # "V/F"
            if self.rep1.checked is True:  # question V/F
                self.rep2.checked = False
            else:
                self.rep2.checked = True
        self.button_modif_color()

    def rep2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.choix == 1: # "V/F"
            if self.rep2.checked is True:  # question V/F
                self.rep1.checked = False
            else:
                self.rep1.checked = True
        self.button_modif_color()
    
    def rep3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_color()
    
    def rep4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_color()
    
    def rep5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_color()

    def drop_down_bareme_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_color()

    





