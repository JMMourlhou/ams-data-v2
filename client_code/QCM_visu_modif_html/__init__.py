from ._anvil_designer import QCM_visu_modif_htmlTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


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
        
        # question
        # module pour ajouter les sauts de pages HTML en modif (les anciens questions en table peuvent encore contenir \n au lieu de <br>)
        qst = self.question_row['question']
        paragraphs = qst.split("\n\n")
        html_list = []
        for p in paragraphs:
            p2 = p.replace("\n", "<br>")  # en HTML \n non reconnu, remplacé par <br>
            html_list.append(f"<p>{p2}</p>")
        html_text = "".join(html_list)

        self.text_area_question.enabled = True
        self.text_area_question.content = html_text  
        
        self.text_box_correction.text = self.question_row['correction']
        
        self.drop_down_bareme.items=["1","2","3","4","5","10"]
        self.drop_down_bareme.selected_value = self.question_row['bareme']                 
       
        if self.question_row['photo'] is not None:
            self.image_1.source = self.question_row['photo']
            #print("--------------------------------------------------------------------------------------------------img ",self.item['photo'])
        else:
            #print("--------------------------------------------------------------------------------------------------img ",self.item['photo'])
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

    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        # self.image_photo.source = file
        thumb_pic = anvil.image.generate_thumbnail(file, 320)
        self.image_photo.source = thumb_pic
        elf.button_modif_color()

    

    def button_modif_color(self, **event_args):                # ========================== Changes
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
                                   self.text_area_question.content,       # question HTML
                                   rep_multi_stagiaire,                   # rep codée ex 10 /  010 ...
                                   self.drop_down_bareme.selected_value,  # Bareme de la question
                                   self.image_1.source,                   # photo
                                   self.text_box_correction.text          # correction en clair
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
