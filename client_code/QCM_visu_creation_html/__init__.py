from ._anvil_designer import QCM_visu_creation_htmlTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js import window
import time


class QCM_visu_creation_html(QCM_visu_creation_htmlTemplate):
    def __init__(self, qcm_row, question_row=None, nb_questions=0, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.qcm_row = qcm_row  # QCM descro row
        self.question_row = question_row  # la question row
        self.type_question = "V/F"
        self.image_1.source = None
        # réponses
        self.rep1.checked = False
        self.rep2.checked = False
        self.rep3.checked = False
        self.rep4.checked = False
        self.rep5.checked = False

        self.rich_text_question.content = ""
        self.rich_text_correction.content = "Correction"
        self.button_question.visible = False
        # num / nb de quesions
        self.label_2.text = ""
        self.label_nb_questions.text = nb_questions
        # Initialisation des drop down nb potions et Barême
        self.drop_down_nb_options.items=([("Vrai/Faux", 1), ("2 options", 2), ("3 options", 3), ("4 options", 4), ("5 options", 5)])
        self.drop_down_bareme.items = ["1", "2", "3", "4", "5", "10"]
        
        #self.drop_down_bareme.selected_value = None
        # =========================================================================================
        # POUR AUTO SAUVEGARDE DU TEXTE:
        # Bouton Validation caché tant que rien n'est modifié
        self.button_validation.visible = False
        self._editor_ready = False

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
        

    # appelé par l'init de cette forme ET l'event du Word_Editor module / timer2
    def _backup_word_editor(self, **e):
        html = e.get("text")
        if not html:
            return

        # --- 1) rien n'a changé ---
        if html == self._last_saved_text:
            return

        self.word_editor_1.text = html

        # Appel EXACTEMENT comme si l'utilisateur cliquait MAIS en mode sov_auto True, on ne sortira pas
        #self.button_validation_click(True)

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

        self.type_question = "V/F"
        self.nb_options = 1
        if self.nb_options > 1:
            if self.type_question == "V/F":
                self.rep1.text = "V"
                self.rep2.text = "F"
            else:  # 2 options possibles, rep1 et rep2 peuvent être identiques  ex 11
                self.rep1.text = "A"
                self.rep2.text = "B"

            if self.question_row["rep_multi"][0:1] == "1":
                self.rep1.checked = True
            else:
                self.rep1.checked = False

            if self.question_row["rep_multi"][1:2] == "1":
                self.rep2.checked = True
            else:
                self.rep2.checked = False

        if self.nb_options > 2:
            self.rep1.text = "A"
            self.rep2.text = "B"
            self.rep3.text = "C"
            self.rep3.visible = True
            if self.question_row["rep_multi"][2:3] == "1":
                self.rep3.checked = True
            else:
                self.rep3.checked = False

        if self.nb_options > 3:
            self.rep4.text = "D"
            self.rep4.visible = True
            if self.question_row["rep_multi"][3:4] == "1":
                self.rep4.checked = True
            else:
                self.rep4.checked = False

        if self.nb_options > 4:
            self.rep5.text = "E"
            self.rep5.visible = True
            if self.question_row["rep_multi"][4:5] == "1":
                self.rep5.checked = True
            else:
                self.rep5.checked = False

        text_not_html = ""
        self.rich_text_correction.visible = False  # Hiding the Correction text
        self.sending_to_word_editor(text_not_html, "question")
        self.button_validation.visible = False

    def button_correction_click(self, **event_args):
        """This method is called when the button is clicked"""
        text_not_html = self.question_row["correction"]
        self.rich_text_question.visible = False  # Hiding the question text
        self.sending_to_word_editor(text_not_html, "correction")
        self.button_validation.visible = False

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
        self.word_editor_1.text = html_text
        self.word_editor_1.form_show()  # will execute the show event in Word_Editor form
        self.word_editor_1.visible = True  # 'Word_Editor' component display

        if self.word_editor_1.param1 == "question":
            self.rich_text_correction.visible = True  # display the Correction Rich Text
            self.rich_text_question.visible = False  # display the Question Rich Text
            self.rich_text_question.content = html_text

        if self.word_editor_1.param1 == "correction":
            self.rich_text_correction.visible = (
                False  # display the Correction Rich Text
            )
            self.rich_text_question.visible = True  # display the Question Rich Text
            self.rich_text_correction.content = html_text

    # handler por afficher le bouton validation uniqt qd text est modifié
    def _arm_editor_ready(self, **e):
        self._editor_ready = True

   

    # Button validation, auto=True qd sauv auto du timer2 de Word_Editor (voir l'init de cette forme)
    def button_validation_click(self, sov_auto=False, **event_args):  # =============  VALIDATION
        """This method is called when the button is clicked"""

        mode = self.word_editor_1.param1  # mode 'modif' /  'creation'
        html = self.word_editor_1.text
        # self.rich_text_correction.scroll_into_view()
        if mode == "question":
            self.rich_text_correction.visible = True  # display the Correction Rich Text
            self.rich_text_question.visible = False  # display the Question Rich Text
            self.rich_text_question.content = html
        if mode == "correction":
            self.rich_text_correction.visible = (
                False  # display the Correction Rich Text
            )
            self.rich_text_question.visible = True  # display the Question Rich Text
            self.rich_text_correction.content = html
            
        #"creation":
        self.button_creer_click(html)

        rep_multi_stagiaire = ""  # CUMUL de la codif des réponses du stagiaire
        if self.type_question == "V/F":
            if self.rep1.checked is True:  # question V/F
                rep_multi_stagiaire = "10"
            else:
                rep_multi_stagiaire = "01"
        else:
            if self.rep1.checked is True:  # question non V/F
                rep_multi_stagiaire = "1"
            else:
                rep_multi_stagiaire = "0"

            if self.nb_options > 1:
                if self.rep2.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"

            if self.nb_options > 2:
                if self.rep3.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"

            if self.nb_options > 3:
                if self.rep4.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"

            if self.nb_options > 4:
                if self.rep5.checked is True:
                    rep_multi_stagiaire = rep_multi_stagiaire + "1"
                else:
                    rep_multi_stagiaire = rep_multi_stagiaire + "0"
        if sov_auto is True:
            with anvil.server.no_loading_indicator:
                result = anvil.server.call(
                    "modif_qcm",
                    self.qcm_row,  # qcm descro row
                    self.question_row["num"],  # num question
                    self.rich_text_question.content,  # question HTML
                    rep_multi_stagiaire,  # rep codée ex 10 /  010 ...
                    self.drop_down_bareme.selected_value,  # Bareme de la question
                    self.image_1.source,  # photo
                    self.rich_text_correction.content,  # correction en clair
                )
        else:
            result = anvil.server.call(
                "modif_qcm",
                self.qcm_row,  # qcm descro row
                self.question_row["num"],  # num question
                self.rich_text_question.content,  # question HTML
                rep_multi_stagiaire,  # rep codée ex 10 /  010 ...
                self.drop_down_bareme.selected_value,  # Bareme de la question
                self.image_1.source,  # photo
                self.rich_text_correction.content,  # correction en clair
            )
        if not result:
            alert("erreur de modification d'une question QCM")
            return
            # j'initialise la forme principale
        else:
            # --- Réinitialisation état ---
            if sov_auto is False:
                # Click manuel sur bt validation on quitte
                # alert('on retourne')
                self.button_retour_click()
            else:
                print("on a sauvé atomatiqt ")
                # sovegarde auto, on ne fait rien
                pass

    

    # ------------------------------------------------------------------
    # Chargement initial du contenu
    # ------------------------------------------------------------------
    def load_qcm_content(self, html):
        self.word_editor_1.set_initial_html(html)

    def button_creer_click(self, text, **event_args):
        """This method is called when the button is clicked"""
        if text == "":
            alert("La question est vide !")
            return
        if self.drop_down_bareme.selected_value is None:
            alert("Choisissez un barême !")
            return
        #qst = text
        #qst = qst.strip()
        question = text

        cor = self.text_box_correction.text
        cor = cor.strip()
        correction = cor
        bareme = int(self.drop_down_bareme.selected_value)
        qcm_nb = self.drop_down_qcm_row.selected_value

        if self.image_1.source != "":
            image = self.image_1.source
        else:
            image = None
        # creation de la réponse multi en fonction du nb d'options choisies +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        reponse = ""
        if self.rep1.checked is True:
            r1 = "1"
        else: 
            r1 = "0"
        if self.rep2.checked is True:
            r2 = "1"
        else: 
            r2 = "0"
        if self.rep3.checked is True:
            r3 = "1"
        else: 
            r3 = "0"
        if self.rep4.checked is True:
            r4 = "1"
        else: 
            r4 = "0"
        if self.rep5.checked is True:
            r5 = "1"
        else: 
            r5 = "0"
        if self.drop_down_nb_options.selected_value == 1 or self.drop_down_nb_options.selected_value == 2:    
            reponse = r1 + r2
        if self.drop_down_nb_options.selected_value == 3:
            reponse = r1 + r2 + r3
        if self.drop_down_nb_options.selected_value == 4:
            reponse = r1 + r2 + r3 + r4
        if self.drop_down_nb_options.selected_value == 5:
            reponse = r1 + r2 + r3 + r4 + r5
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  NUM question   +++++++++++++++++++++++++++++
        num = int(self.label_2.text) #je connais le num de question à changer
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  type de question   +++++++++++++++++++++++++++++
        if self.drop_down_nb_options.selected_value == 1:    # type V/F
            type = "V/F"       # rep1 ou rep2 peuvent être vrai
        else:
            type = "Multi"     # rep1 et rep2 peuvent être vrai 
            
        # param (descro du QCM)
        param = self.drop_down_qcm_row.selected_value["destination"]
                    
        # je récupère mes variables globales  question, reponse, bareme
        result = anvil.server.call("add_ligne_qcm", num, question, correction, reponse, bareme, image, qcm_nb, type, param)         #num du stage  de la ligne
        if result:
            n = Notification("Création de la question !",
                 timeout=1)   # par défaut 2 secondes
            n.show()
            # raffraichit les lignes qcm en récupérant le choix du qcm ds la dropdown
            from anvil import open_form       # j'initialise la forme principale avec le choix du qcm ds la dropdown
            open_form("QCM_visu_modif_Main", qcm_nb)
        else:
            alert("erreur de création d'une question QCM")

    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        thumb_pic = anvil.image.generate_thumbnail(file, 640)
        self.image_1.source = thumb_pic
        self.button_modif_color()

    def drop_down_nb_options_change(self, **event_args):
        """This method is called when an item is selected"""
        self.rep1.checked = False
        self.rep2.checked = False
        self.rep3.checked = False
        self.rep4.checked = False
        self.rep5.checked = False
        choix = self.drop_down_nb_options.selected_value
        #print(choix, type(choix))
        question_part1 = """<!-- Question -->
                            <p
                            style="
                                margin-bottom: 10px;
                                text-align: left;
                                font-weight: bold;
                                color: rgb(0, 192, 250);
                            "
                            >
                            <span
                                style="
                                background-color: var(--anvil-color-On-Secondary-Container-94f5);
                                padding: 2px 6px;
                                border-radius: 4px;
                                margin-right: 6px;
                                "
                                <Question ici>
                            </span>
                            
                            </p>
                        """

        if choix == 1:   # Vrai/ Faux    l'1 ou l'autre, rep1 et rep2 ne peuvent pas  être identiques
            self.rich_text_question.content = question_part1
            self.rep3.visible = False
            self.rep4.visible = False
            self.rep5.visible = False
            self.rep1.text = "Vrai"
            self.rep2.text = "Faux"
            self.word_editor_1.text = question_part1

        if choix > 1:     # 2 options possibles, rep1 et rep2 peuvent être identiques  ex 11 
            self.rep1.text = "A"
            self.rep2.text = "B"
            self.rep3.visible = False
            self.rep4.visible = False
            self.rep5.visible = False
            self.rich_text_question.content  = "titre\n\nA  .\n\nB  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        </ul>
                                    """

        if choix > 2:     # au moins 3 options possibles, rep1 à rep3 peuvent être identiques  ex 111
            self.rep3.visible = True
            self.rep4.visible = False
            self.rep5.visible = False
            self.rich_text_question.content  = "titre\n\nA  .\nB  .\nC  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        <li>C</li>
                                        </ul>
                                    """
        if choix > 3:     # au moins 4 options possibles, rep1 et rep4 peuvent être identiques  ex  1111
            self.rep4.visible = True
            self.rep5.visible = False
            self.rich_text_question.content  = "titre\n\nA  .\nB  .\nC  .\nD  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        <li>C</li>
                                        <li>D</li>
                                        </ul>
                                    """
        if choix > 4:     # 5 options possibles, rep1 à rep2 peuvent être identiques
            self.rep5.visible = True
            self.rich_text_question.content = "titre\n\nA  .\nB  .\nC  .\nD  .\nE  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        <li>C</li>
                                        <li>D</li>
                                        <li>E</li>
                                        </ul>
                                    """

        # -----------------------------------------------------------------------
        
        self.button_modif_color()

    def rep1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.type_question == "V/F":
            if self.rep1.checked is True:  # question V/F
                self.rep2.checked = False
            else:
                self.rep2.checked = True
        self.button_modif_color()

    def rep2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.type_question == "V/F":
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

    def button_retour_click(self, **event_args):  # =============  RETOUR
        """This method is called when the button is clicked"""
        qcm_descro_nb = self.qcm_row
        open_form("QCM_visu_modif_Main", qcm_descro_nb)

