from ._anvil_designer import QCM_visu_modif_htmlTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js import window

class QCM_visu_modif_html(QCM_visu_modif_htmlTemplate):
    def __init__(self, qcm_row, question_row, nb_questions, **properties):  
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.qcm_row = qcm_row              # QCM descro row
        self.question_row = question_row    # la question row

        # num / nb de quesions
        self.label_2.text = self.question_row['num']
        self.label_nb_questions.text = nb_questions
        
        
        
        self.drop_down_bareme.items=["1","2","3","4","5","10"]
        self.drop_down_bareme.selected_value = self.question_row['bareme']                 
       
        if self.question_row['photo'] is not None:
            self.image_1.source = self.question_row['photo']
        else:
            self.image_1.source = None
            self.cp_img.visible = False
            self.image_1.visible = False
            
        self.type_question = self.question_row['type']  
        self.nb_options = len(self.question_row['rep_multi'])     # je sais combien d'options j'utilise pour cette question
        if self.nb_options > 1:     
            if self.type_question == "V/F":
                self.rep1.text = "V"
                self.rep2.text = "F"
            else:                   # 2 options possibles, rep1 et rep2 peuvent être identiques  ex 11 
                self.rep1.text = "A"
                self.rep2.text = "B"
                
            if self.question_row['rep_multi'][0:1]  == "1":
                self.rep1.checked = True      
            else:
                self.rep1.checked = False

            if self.question_row['rep_multi'][1:2]  == "1":
                self.rep2.checked = True      
            else:
                self.rep2.checked = False

        if self.nb_options > 2:
            self.rep1.text = "A"
            self.rep2.text = "B"
            self.rep3.text = "C"
            self.rep3.visible = True
            if self.question_row['rep_multi'][2:3]  == "1":
                self.rep3.checked = True      
            else:
                self.rep3.checked = False

        if self.nb_options > 3:        
            self.rep4.text = "D"
            self.rep4.visible = True
            if self.question_row['rep_multi'][3:4]  == "1":
                self.rep4.checked = True      
            else:
                self.rep4.checked = False

        if self.nb_options > 4:
            self.rep5.text = "E"
            self.rep5.visible = True
            if self.question_row['rep_multi'][4:5]  == "1":
                self.rep5.checked = True      
            else:
                self.rep5.checked = False
                
        
        self.rich_text_correction.content = self.question_row['correction']
        self.rich_text_question.content = self.question_row['question']
        self.rich_text_question.visible = False
        self.word_editor_1.scroll_into_view()
        self.button_question_click() # on affiche la question
        
                
    
    def button_question_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        self.type_question = self.question_row['type']  
        self.nb_options = len(self.question_row['rep_multi'])     # je sais combien d'options j'utilise pour cette question
        if self.nb_options > 1:     
            if self.type_question == "V/F":
                self.rep1.text = "V"
                self.rep2.text = "F"
            else:                   # 2 options possibles, rep1 et rep2 peuvent être identiques  ex 11 
                self.rep1.text = "A"
                self.rep2.text = "B"

            if self.question_row['rep_multi'][0:1]  == "1":
                self.rep1.checked = True      
            else:
                self.rep1.checked = False

            if self.question_row['rep_multi'][1:2]  == "1":
                self.rep2.checked = True      
            else:
                self.rep2.checked = False

        if self.nb_options > 2:
            self.rep1.text = "A"
            self.rep2.text = "B"
            self.rep3.text = "C"
            self.rep3.visible = True
            if self.question_row['rep_multi'][2:3]  == "1":
                self.rep3.checked = True      
            else:
                self.rep3.checked = False

        if self.nb_options > 3:        
            self.rep4.text = "D"
            self.rep4.visible = True
            if self.question_row['rep_multi'][3:4]  == "1":
                self.rep4.checked = True      
            else:
                self.rep4.checked = False

        if self.nb_options > 4:
            self.rep5.text = "E"
            self.rep5.visible = True
            if self.question_row['rep_multi'][4:5]  == "1":
                self.rep5.checked = True      
            else:
                self.rep5.checked = False
        
        text_not_html = self.question_row['question']
        self.rich_text_correction.visible = False      # Hiding the Correction text
        self.sending_to_word_editor(text_not_html, "question")

    def button_correction_click(self, **event_args):
        """This method is called when the button is clicked"""
        text_not_html = self.question_row['correction']
        self.rich_text_question.visible = False      # Hiding the question text
        self.sending_to_word_editor(text_not_html, "correction")

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
        else :
            self.word_editor_1.bt_valid_text = "Validat°"   
            self.word_editor_1.bt_exit_text = "Sortie"
        # Word_Editor PDF download titles parameters:
        self.word_editor_1.top_ligne_2 = f"Question N° {self.question_row['num']} "
        self.top_ligne_2 = self.top_ligne_1 = f"QCM {self.qcm_row['destination']} "
        
        # Text to be modified by Word_Editor
        self.word_editor_1.remove_on_exit = False
        self.word_editor_1.param1 = type_text   # 'question' or 'correction'
        self.word_editor_1.text = html_text
        self.word_editor_1.form_show() # will execute the show event in Word_Editor form
        self.word_editor_1.visible = True  # 'Word_Editor' component display
       
        self.word_editor_1.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked

    """
    #===================================================================================================================================================
    RETOUR DU WORD EDITOR  
    # ==================================================================================================================================================
    """
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form (modif du text de base de l'évènement)
    def handle_click_fin_saisie(self, sender, **event_args):
        # sender.text contains the 'Word_editor'form's HTML text
        mode = sender.param1       # mode 'modif' /  'creation' 
        #alert(sender.text)
        #alert(mode)
        self.text = sender.text    # texte html de lévenement
        #self.content_panel.clear()  #effacement du content_panel
        self.rich_text_question.visible = True       # display the Question Rich Text
        self.rich_text_correction.visible = True      # display the Correction Rich Text
        self.rich_text_correction.scroll_into_view()
        if mode == "question":
            self.rich_text_question.content = sender.text
        if mode == "correction":
            self.rich_text_correction.content = sender.text
        self.button_modif_color()
        if mode == "creation":
            self.button_creer_click(self.text)
        if mode == "exit":
            self.button_retour_click()
    """
    Fin RETOUR DU WORD EDITOR  
    """  

    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        # self.image_photo.source = file
        thumb_pic = anvil.image.generate_thumbnail(file, 320)
        self.image_photo.source = thumb_pic
        self.button_modif_color()

    

    def button_modif_color(self, **event_args):                # ========================== Changes
        self.button_modif.visible = True
        self.button_modif.enabled = True
        self.button_modif.background = "red"
        self.button_modif.foreground = "yellow"

    def rep1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.type_question == "V/F":
            if self.rep1.checked is True:   # question V/F
                self.rep2.checked = False
            else:
                self.rep2.checked = True
        self.button_modif_color()
        

    def rep2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.type_question == "V/F":
            if self.rep2.checked is True:   # question V/F
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

    def text_box_correction_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.button_modif_color()

    def drop_down_bareme_change(self, **event_args):                             
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif_color()
        

    def button_modif_click(self, **event_args):                                         # =============  VALIDATION
        """This method is called when the button is clicked"""

        rep_multi_stagiaire = ""                              # CUMUL de la codif des réponses du stagiaire
        if self.type_question == "V/F":
            if self.rep1.checked is True:   # question V/F
                rep_multi_stagiaire = "10"
            else:
                rep_multi_stagiaire = "01"
        else:
            if self.rep1.checked is True:   # question non V/F
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
                        
        result = anvil.server.call('modif_qcm',
                                   self.qcm_row,                          # qcm descro row
                                   self.question_row['num'],              # num question
                                   self.rich_text_question.content,       # question HTML
                                   rep_multi_stagiaire,                   # rep codée ex 10 /  010 ...
                                   self.drop_down_bareme.selected_value,  # Bareme de la question
                                   self.image_1.source,                   # photo
                                   self.rich_text_correction.content      # correction en clair
                                  ) 
        if not result:
            alert("erreur de modification d'une question QCM")
            return
            # j'initialise la forme principale
        else:
            self.button_retour_click()

    def button_retour_click(self, **event_args):                                        # =============  RETOUR
        """This method is called when the button is clicked"""
        qcm_descro_nb = self.qcm_row
        open_form('QCM_visu_modif_Main', qcm_descro_nb)

    

   
