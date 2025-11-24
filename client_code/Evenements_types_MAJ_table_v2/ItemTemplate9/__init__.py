from ._anvil_designer import ItemTemplate9Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Word_editor import Word_editor   # Word processor component inséré ds self.content_panel

class ItemTemplate9(ItemTemplate9Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.text = self.item['type']
        self.text_box_2.text = self.item['code']
        self.text_box_3.text = self.item['msg_0']
        self.text_box_4.text = self.item['msg_1']
        self.check_box_1.checked = self.item['mot_clef_setup']

        self.sov_text_box_1 = self.item['type']
        self.sov_text_box_2 = self.item['code']
        self.sov_text_box_3 = self.item['msg_0']
        self.sov_text_box_4 = self.item['msg_1']
        self.sov_text = self.item['text_initial']
        self.sov_check_box_1 = self.item['mot_clef_setup']

        self.nb = int(self.text_box_2.text)

        """
        =============================================================================================================================================      CALL FOR THE WORD EDITOR
        """
        # INSERTION TEXT-EDITOR form 'Word_editor'  (voir import)
        alert(self.item['text_initial'])
        text_editor = Word_editor()
        text_editor.text = self.item['text_initial']   # .text: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        text_editor.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        #text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 15 sec, timer_2 de la form Word_editor
        self.content_panel.add_component(text_editor)
        """
        =================================================================================================================================================================================
        """

    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form
    def handle_click_fin_saisie(self, sender, **event_args):
        # sender.text contains the 'Word_editor'form's HTML text
        print(sender.text)
        self.validation(False, sender.text)
        print(sender.text)

    def validation(self, text, **event_args):
        """This method is called when the button is clicked"""

        # tests sur le code du type d'évenement -----------------------------    
        # Text_box_2 (code) vide ? 
        if self.text_box_2.text == "":
            alert("Entrez un code !")
            self.text_box_2.focus()
            return

        # Code existant en dehors de lui ?
        test = app_tables.event_types.search(code=int(self.text_box_2.text))
        if len(test)==1 and self.text_box_2.text != str(self.sov_text_box_2):   # self.sov_text_box_2   est int
            alert("Ce code est déjà pris !")
            self.text_box_2.focus()
            return

        # je ne test pas le code 0 qui ne contient pas de texte dans les colonnes en dehors de code et msg1 
        if self.sov_text_box_2 != 0:   
            # Text_box_1 (type evnt) non vide
            if self.text_box_1.text == "" or len(self.text_box_1.text) < 5:
                alert("Entrez un type d'évenement clair (> à 5 caractères")
                self.text_box_1.focus()
                return    

            # Text_box_3 (msg 0)non vide  ------------------------------------------------------------
            if self.text_box_3.text == "" or len(self.text_box_3.text) < 6:
                alert("Entrez le message qui apparaîtra dans le 1er menu ! (au moins 6 caractères)")
                self.text_box_3.focus()
                return

            # Text_box_4 (msg 1)non vide
            if self.text_box_4.text == "" or len(self.text_box_4.text) < 6:
                alert("Entrez le message qui apparaîtra dans le 2eme menu ! (au moins 6 caractères)")
                self.text_box_4.focus()
                return   


        r=alert("Voulez-vous vraiment modifier ce type d'évenement ?",buttons=[("oui",True),("non",False)])
        if r :   # oui
            nb = int(self.text_box_2.text)
            result = anvil.server.call("modif_type_evnt", self.item, self.text_box_1.text,
                                       nb,
                                       self.text_box_3.text,
                                       self.text_box_4.text,
                                       text,
                                       self.check_box_1.checked               
                                      )
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert("Modification effectuée !")

        else:   # non
            self.text_box_1.text = self.sov_text_box_1 
            self.text_box_2.text = self.sov_text_box_2
            self.text_box_3.text = self.sov_text_box_3 
            self.text_box_4.text = self.sov_text_box_4
            self.text_area_1.text = self.sov_text
            self.check_box_1.checked = self.sov_check_box_1 

        self.button_modif.visible = False
        open_form("Evenements_types_MAJ_table_v2")