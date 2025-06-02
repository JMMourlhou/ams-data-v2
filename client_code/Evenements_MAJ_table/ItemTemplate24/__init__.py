from ._anvil_designer import ItemTemplate24Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate24(ItemTemplate24Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.text_box_1.text = self.item['type']
        self.text_box_2.text = self.item['code']
        self.text_box_3.text = self.item['msg_0']
        self.text_box_4.text = self.item['msg_1']
        self.text_area_1.text = self.item['text_initial']
        self.check_box_1.checked = self.item['mot_clef_setup']
        
        self.sov_text_box_1 = self.item['type']
        self.sov_text_box_2 = self.item['code']
        self.sov_text_box_3 = self.item['msg_0']
        self.sov_text_box_4 = self.item['msg_1']
        self.sov_text_area_1 = self.item['text_initial']
        self.sov_check_box_1 = self.item['mot_clef_setup']
        
        self.nb = int(self.text_box_2.text)
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        
        # j'empêche d'effacer les codes 0 à 3
        if self.nb < 4:
            alert("Ce type d'évenement ne peut être effacé !")
            return

        test = app_tables.events.search(event_typ=self.item)
        if len(test)>0:
            alert(f"Attention, il y a déja {len(test)} évenement(s) enregistré(s)  pour cette catégorie !\n\nEffacez les d'abord avant de détruire cette catégorie d'évenements !")
            return
            
        r=alert("Voulez-vous vraiment effacer ce type d'évenement ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result = anvil.server.call("del_type_evnt", self.item)
            if result is not True:
                alert("Erreur: Effacement non effectué !")
                return
            alert("Effacement effectué !")
        open_form("Evenements_MAJ_table")

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def button_modif_click(self, **event_args):
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
                                                                self.text_area_1.text,
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
            self.text_area_1.text = self.sov_text_area_1 
            self.check_box_1.checked = self.sov_check_box_1 
        
        self.button_modif.visible = False
        open_form("Evenements_MAJ_table")