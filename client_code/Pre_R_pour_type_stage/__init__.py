from ._anvil_designer import Pre_R_pour_type_stageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

global code_stage
code_stage = ""

global dico_pre_requis
dico_pre_requis = {}

class Pre_R_pour_type_stage(Pre_R_pour_type_stageTemplate):
    def __init__(self, code_stage="",**properties):             # code stage si vient d'annulation d'un pré_requis ds R.RowTemplate1
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        
        # Drop down codes stages
        liste = [(r['code'], r) for r in app_tables.codes_stages.search(tables.order_by("code", ascending=True))]   
        self.drop_down_code_stage.items = liste
        
        if code_stage != "":  # si vient d'annulation d'un pré_requis ds R.RowTemplate1, je pre selectionne la dropdown stage
            row = app_tables.codes_stages.get(code=code_stage)
            self.drop_down_code_stage.selected_value = row
            self.drop_down_code_stage_change()
       
    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        #lecture du dictionaire ds table codes_stages pour le stage sélectionné
        
        row = self.drop_down_code_stage.selected_value
        self.row = row
        if row is None :
            alert("Vous devez sélectionner un stage !")
            self.drop_down_code_stage.focus()
            return
        
        global code_stage
        code_stage = row["code"]
        
        # lecture du dictionaire des pré requis pour ce type de stage 
        global dico_pre_requis
        dico_pre_requis = row["pre_requis"]
        
        if row['pre_requis'] is None:  # si le dictionaire n'existe pas encore (pas de pré requis encore introduit pour ce type de stage)
            dico_pre_requis = {}

        if isinstance(row['pre_requis'], dict):       # LE DICT EXISTE DS TABLE CODES STAGE, row du stage (pré requis introduits pour ce type de stage))
            # INITIALISATION Drop down pré-requis en fonction des pré requis déjà sélectionnés ds dico
            dico_pre_requis = row['pre_requis']
            
        self.drop_down_pre_requis.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if not dico_pre_requis.get(r["code_pre_requis"])]
        self.drop_down_pre_requis.visible = True
            
        # affichage du repeating panel des prérequis à partir du dico que je transforme  en liste
        list_keys = dico_pre_requis.keys()
        list_keys = sorted(list_keys)  # création de la liste triée des clefs du dictionaires prérequis
        # j'affiche tous les pré requis 
        print(len(list_keys))
        self.repeating_panel_1.items = list(list_keys)   # liste des clefs (pré requis)
            
        self.sov_dico_ds_temp()   # sauvegarde du dico ds TABLE TEMP
            
        
    def drop_down_pre_requis_change(self, **event_args):
        """This method is called when an item is selected"""
        row = self.drop_down_pre_requis.selected_value       # row du pre_requis 
        if row is None:
            alert("Vous devez sélectionner un pré-requis !")
            self.drop_down_code_stage.focus()
            return
        else:
            clef = row["code_pre_requis"]  #extraction de la clef à ajouter à partir de la row sélectionnée de la dropbox
        # rajout clef/valeur ds dico 
        global dico_pre_requis
        dico_pre_requis[clef]= {                        # AJOUT DE LA CLEF DS LE DICO
                                "Doc": row["doc"],
                                "Validé": False,
                                "Commentaires": "",
                                "Nom_document": ""
                                }

        #réaffichage des pré requis
        list_keys = dico_pre_requis.keys()
        list_keys = sorted(list_keys)  # création de la liste triée des clefs du dictionaires prérequis
        print(list_keys)
        self.repeating_panel_1.items = list(list_keys)   # liste des clefs (pré requis)
        
        #réinitialisation dropdown pré requis sans le pré requis sélectionné
        self.drop_down_pre_requis.items = [(r["requis"], r) for r in app_tables.pre_requis.search(tables.order_by("requis", ascending=True)) if not dico_pre_requis.get(r["code_pre_requis"])]
        
        global code_stage
        result = anvil.server.call("modif_pre_requis_codes_stages", code_stage, dico_pre_requis)

        self.sov_dico_ds_temp()   # sauvegarde du dico ds TABLE TEMP   
        # =================================================================================================
        r=alert("Voulez-vous ajouter ce pré-requis pour tous les stagiaires de ce type de stage ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # Oui
            #liste_stages = app_tables.stages.search(code_txt = code_stage)  # PAS FIABLE CAR BASE SUR UNE DONNEE TEXTE !
            
            liste_stages = app_tables.stages.search(code = self.row)  # row stage
            print("nb de stages: ",len(liste_stages))
            # acquisition des stagiaires inscrits à ces stages
            for stage in liste_stages:
                print(stage['numero'])
                liste_stagiaires = app_tables.stagiaires_inscrits.search(numero=stage['numero'])
                # Pour chq stagiaire, ajout du pré_requis
                for stagiaire in liste_stagiaires:
                    #print(stagiaire["name"])
                    # ajout du pré_requis si pas existant
                    test = app_tables.pre_requis_stagiaire.search(stage_num = stage,
                                                                item_requis = row,
                                                                stagiaire_email = stagiaire['user_email'])
                    #print("lg: ", len(test))
                    if len(test) == 0:
                        #print("non existant")
                        result = anvil.server.call("add_1_pre_requis", stage, stagiaire['user_email']['email'], row)
            print("TEST !  : ", result)
            if result:
                alert("Ajout effectué !")
            else:
                alert("Erreur en ajout !")
                    
                
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")

    
    def sov_dico_ds_temp(self, **event_args):
        table_temp = app_tables.temp.search()[0]   # sauvegarde du dico ds TABLE TEMP
        global code_stage
        global dico_pre_requis
        table_temp.update(pre_r_pour_stage = dico_pre_requis,
                            code_stage = code_stage
                            )




    




