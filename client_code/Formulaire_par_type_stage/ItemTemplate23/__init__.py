from ._anvil_designer import ItemTemplate23Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class ItemTemplate23(ItemTemplate23Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # récupération de la forme mère par  self.f = get_open_form() en init
        self.f = get_open_form()   # récupération de la forme mère pour accéder aux fonctions et composents
        #print("form mère atteingnable (en modif): ", self.f) 
        
        # Any code you write here will run before the form opens.
        self.text_box_1.text = "  " + self.item[0]
        self.text_box_2.text = "  "  + self.item[1]
        
        if self.item[2] == "obligatoire":
            self.check_box_1.checked = True
        else:
            self.check_box_1.checked = False
            
        self.button_annuler.tag = self.item[0] # 1,2,3 ...
        self.button_modif.tag = self.item[0] # 1,2,3 ...
            
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment enlever ce texte du formulaire ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            row_temp=app_tables.temp.search()[0]         # lecture fichier temp du dico utilisé
            dico_formulaire=row_temp['dico_formulaire']
            key=self.button_annuler.tag
            del dico_formulaire[key]

            # renumériser les clés des questions car une question a pu être enlevée en template 23
            # j'utilise un dictionaire temporaire dico_temp
            dico_temp = {}
            i=1
            for key, valeur in dico_formulaire.items():  #lecture à partir de la liste des clés
                key_temp = str(i)
                dico_temp[key_temp] = [                          # AJOUT DE LA CLEF DS LE DICO
                                    valeur[0],     # texte question 
                                    valeur[1],     # oblig
                                    valeur[2],     # code texte
                                    ]
                i += 1
            dico_formulaire = dico_temp

            # sauvegarde 
            self.f.sov_dico(dico_formulaire)  
        # réouverure de la forme mère pour actualisation de l'affichage    
        code_stage_row = self.f.drop_down_code_stage.selected_value
        type_formulaire = self.f.drop_down_type_formulaire.selected_value
        open_form("Formulaire_par_type_stage", code_stage_row, type_formulaire)
        
    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment modifier cette question du formulaire ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            row_temp=app_tables.temp.search()[0]
            dico_formulaire=row_temp['dico_formulaire']
            key=self.button_modif.tag
            dico_formulaire[key]
            obl = ""
            if self.check_box_1.checked is True:
                obl = "obligatoire"
            else:
                obl = "facultative"
            dico_formulaire[key] = [                          # AJOUT DE LA CLEF DS LE DICO
                                self.text_box_2.text,
                                obl,
                                self.item[3]
                                ]
        
            # sauvegarde
            self.f.sov_dico(dico_formulaire)  
        # réouverure de la forme mère pour actualisation de l'affichage     
        code_stage_row = self.f.drop_down_code_stage.selected_value
        type_formulaire = self.f.drop_down_type_formulaire.selected_value
        open_form("Formulaire_par_type_stage", code_stage_row, type_formulaire)
        
    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def check_box_1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_modif.visible = True
