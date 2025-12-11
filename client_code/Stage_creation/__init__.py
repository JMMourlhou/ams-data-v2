from ._anvil_designer import Stage_creationTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from anvil import open_form
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML

class Stage_creation(Stage_creationTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
       
        # Any code you write here will run before the form opens.
        
        self.button_qr_code_display.visible = False
        # Numéro de stage
        num = app_tables.cpt_stages.search()[0]
        cpt=int(num['compteur'])+1
        self.text_box_num_stage.text=cpt
        
        # Drop down codes stages
        self.drop_down_code_stage.items = [(r['code'], r) for r in app_tables.codes_stages.search(tables.order_by("code", ascending=True))]

        # Drop down codes lieux
        self.drop_down_lieux.items = [(r['lieu'], r) for r in app_tables.lieux.search()]

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        row = self.drop_down_code_stage.selected_value
        if row is None :
            alert("Vous devez sélectionner un stage !")
            self.drop_down_code_stage.focus()
            return
        self.text_box_intitule.text=row['intitulé']

    def date_picker_to_change(self, **event_args):
        """This method is called when the selected date changes"""
        date1 = self.date_picker_to.date
        date2 = self.date_picker_from.date
        if date2 is None:  # 1ere date vide
            alert("La date de fin est inférieure à la date de début !")
            self.date_picker_from.focus()
        if date1 < date2 :
            alert("La date de fin est inférieure à la date de début !")
            self.date_picker_to.focus()
    
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_stages import Visu_stages
        open_form('Visu_stages')

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        """ Tests avant validation """     
               
        row = self.drop_down_code_stage.selected_value    # Récupération de la ligne stage sélectionnée
        if row is None:
            alert("Entrez le code du stage")
            return
        row2 = self.drop_down_lieux.selected_value         # Récupération du lieu sélectionné
        if row2 is None:
            alert("Entrez le lieu du stage")
            return

        if self.date_picker_to.date is None :           # dates vides ?
            alert("Entrez la date de fin du stage")
            return
        if self.date_picker_from.date is None :     
            alert("Entrez la date de début du stage")
            return
        self.drop_down_code_stage_change()      #test si date fin > date début
       
        # Test si numero stage code existant
        stage=None
        stage = app_tables.stages.search(numero=int(self.text_box_num_stage.text))
        if len(stage)>0:
            alert("Le numéro de stage existe déjà !")
            return
            
        #result = anvil.server.call("add_stage", row['code'],         #num du stage  de la ligne 
        result = anvil.server.call("add_stage", row,         # row  table codes_stages
                                                row['code'], # code stage en clair, txt (ex: 'PSC1')
                                                self.text_box_num_stage.text,
                                                row2,        # row table lieu
                                                self.date_picker_from.date,
                                                self.text_box_nb_stagiaires_deb.text,
                                                self.date_picker_to.date,
                                                self.text_box_nb_stagiaires_fin.text,               # extraction du type de stga de la ligne dropdown    
                                                self.text_box_nb_stagiaires_diplom.text,
                                                self.text_area_commentaires.text,
                                                self.text_box_pv.text
                                                 )
        if result is True :
            AlertHTML.success("Succès", "Stage créé !")
        else :
            AlertHTML.error("Erreur", f"Stage non créé !<br><br> {result}")
        self.button_annuler_click()

    def button_qr_code_display_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('QrCode_display', False, self.text_box_num_stage.text) # False = en création de stage, j'affiche le qr code

    def date_picker_from_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True

    def drop_down_lieux_change(self, **event_args):
        """This method is called when an item is selected"""
        self.button_validation.visible = True

    def text_box_nb_stagiaires_deb_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True

    def text_box_nb_stagiaires_fin_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True

    def text_box_nb_stagiaires_diplom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_validation.visible = True

    def text_area_commentaires_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.button_validation.visible = True

    def text_box_pv_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.button_validation.visible = True







                                   

      


