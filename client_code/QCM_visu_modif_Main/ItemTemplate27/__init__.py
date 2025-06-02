from ._anvil_designer import ItemTemplate27Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate27(ItemTemplate27Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.button_descro.text = str(self.item[1]) + " - " + self.item[2]   # si la liste a été construite car qcm existant
            
    def button_descro_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.button_send.visible is False:
            self.button_send.visible = True
        else:
            self.button_send.visible = False

    def button_send_click(self, **event_args):
        """This method is called when the button is clicked"""
        # écriture du nouveau qcm enfant dans le dictionaire
        # self.sov_qcm_nb contient le qcm à ajouter dans le dico
        #                                        qcm_exam_row,    qcm_enfant_nb,        nb_questions
        result = anvil.server.call("qcm_enfant_add", self.item[0],    str(self.item[1]),      0)    # qcm_exam_row
        if result is True:
            alert("Ajout du qcm enfant effectué!\n\nAjoutez le nb de questions allouées à ce Qcm enfant")
            # réaffichage après maj du dico avec le row du Qcm sur lequel je travaille
            open_form('QCM_visu_modif_Main', self.item[0])
        else:
            alert("Ajout du qcm enfant non effectué!")
            return
            