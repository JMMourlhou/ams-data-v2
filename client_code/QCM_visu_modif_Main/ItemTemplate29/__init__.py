from ._anvil_designer import ItemTemplate29Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate29(ItemTemplate29Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        #                              0             1              2                 3
        #                              qcm_exam_row    , qcm enfant nb, qcm_destination,  nb de questions
        self.button_qcm_enfant.text = str(self.item[1]) + " - " + self.item[2] 
        nb_questions_qcm_enfant = self.item[3]
        if nb_questions_qcm_enfant == "0":
            
            self.text_box_nb_questions.background = "red"
            self.text_box_nb_questions.foreground = "yellow"
        self.text_box_nb_questions.text = nb_questions_qcm_enfant

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        # enlever le qcm enfant du dictionaire source en table qcm_description
        # self.sov_qcm_nb contient le qcm à elever du dico
        #                                        qcm_exam_row,    qcm_enfant_nb,      
        result = anvil.server.call("qcm_enfant_del", self.item[0],    str(self.item[1]))    # qcm_exam_row
        if result is True:
            alert("Effacement du qcm enfant effectué!")
            # réaffichage après maj du dico avec le row du Qcm sur lequel je travaille
            open_form('QCM_visu_modif_Main', self.item[0])
        else:
            alert("Effacement du qcm enfant non effectué!")
            return

    def button_descro_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.button_del.visible is False:
            self.button_del.visible = True
        else:
            self.button_del.visible = False


    def text_box_nb_questions_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        # écriture du nb de questions du qcm enfant dans le dictionaire
        # self.sov_qcm_nb contient le qcm à ajouter dans le dico
        #                                        qcm_exam_row,    qcm_enfant_nb,              nb_questions
        result = anvil.server.call("qcm_enfant_add", self.item[0],    str(self.item[1]),      self.text_box_nb_questions.text)    # qcm_exam_row
        if result is True:
            alert("Modification du nb de questions qcm enfant effectué! ")
            # réaffichage après maj du dico avec le row du Qcm sur lequel je travaille
            open_form('QCM_visu_modif_Main', self.item[0])
        else:
            alert("Modif du nb de questions du Qcm enfant non effectué!")
            return

    def text_box_nb_questions_change(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_valid.visible=True

    def button_valid_click(self, **event_args):
        """This method is called when the button is clicked"""
        # écriture du nb de questions du qcm enfant dans le dictionaire
        # self.sov_qcm_nb contient le qcm à ajouter dans le dico
        #                                        qcm_exam_row,    qcm_enfant_nb,              nb_questions
        result = anvil.server.call("qcm_enfant_add", self.item[0],    str(self.item[1]),      self.text_box_nb_questions.text)    # qcm_exam_row
        if result is True:
            alert("Modification du nb de questions qcm enfant effectué! ")
            # réaffichage après maj du dico avec le row du Qcm sur lequel je travaille
            open_form('QCM_visu_modif_Main', self.item[0])
        else:
            alert("Modif du nb de questions du Qcm enfant non effectué!")
            