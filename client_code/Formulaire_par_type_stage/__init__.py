from ._anvil_designer import Formulaire_par_type_stageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

global dico_formulaire
dico_formulaire = {}

global dico_test
dico_test = {}

class Formulaire_par_type_stage(Formulaire_par_type_stageTemplate):
    def __init__(self, code_stage="", type_formulaire="", **properties):  # code stage si vient d'annulation d'un pré_requis ds R.RowTemplate1
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.label_sov_dico.text = {}
        
        # si code_stage="" = "", c'est une ouverture normale
        # initilistaion du dico_formulaire ds TABLE TEMP    
        table_temp = app_tables.temp.search()[0]  # sauvegarde du dico ds TABLE TEMP
        table_temp.update(dico_formulaire={})
        
        # Initialisation drop down codes stages
        liste = [(r["code"], r)for r in app_tables.codes_stages.search(tables.order_by("code", ascending=True))]
        self.drop_down_code_stage.items = liste
        if code_stage != "":  # si vient d'annulation d'un pré_requis ds R.RowTemplate1, je pre selectionne la dropdown stage
            self.row_stage = app_tables.codes_stages.get(code=code_stage['code'])
            self.drop_down_code_stage.selected_value = self.row_stage
        if type_formulaire != "":
            self.drop_down_type_formulaire.selected_value = type_formulaire
            self.drop_down_type_formulaire.visible = True
            self.drop_down_type_formulaire_change()

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        # lecture du dictionaire ds table codes_stages pour le stage sélectionné
        self.drop_down_type_formulaire.selected_value = None
        self.row_stage = self.drop_down_code_stage.selected_value
        if self.row_stage is None:
            alert("Vous devez sélectionner un stage !")
            self.drop_down_code_stage.focus()
            return
        self.drop_down_type_formulaire.visible = True
        self.repeating_panel_2.visible = False
        self.drop_down_textes_formulaire.visible = False
         
    def drop_down_type_formulaire_change(self, **event_args):
        """This method is called when an item is selected"""
        # initilistaion du dico_formulaire ds TABLE TEMP    
        table_temp = app_tables.temp.search()[0]  # sauvegarde du dico ds TABLE TEMP
        table_temp.update(dico_formulaire={})
        # initilisation du drop down formulaire
        self.drop_down_textes_formulaire.selected_value = None
        self.repeating_panel_2.visible = False
        global dico_formulaire
        type_formulaire = self.drop_down_type_formulaire.selected_value
        type_formulaire = type_formulaire[0:5]
        
        # initialisation de la liste des textes formulaires de la table texte_formulaires
        # lecture du dictionaire pour ce type de stage et type de formulaire
        if type_formulaire == "SAT_F":
            dico_formulaire = self.row_stage["satisf_q_ferm_template"]
            self.dico_test_setup(dico_formulaire)
        if type_formulaire == "SAT_O":
            dico_formulaire = self.row_stage["satisf_q_ouv_template"]
            self.dico_test_setup(dico_formulaire)
        if type_formulaire == "SUI_F":
            dico_formulaire = self.row_stage["suivi_stage_q_ferm_template"]
            self.dico_test_setup(dico_formulaire)
        if type_formulaire == "SUI_O":
            dico_formulaire = self.row_stage["suivi_stage_q_ouv_template"]
            self.dico_test_setup(dico_formulaire)
        if type_formulaire == "COM_F":
            dico_formulaire = self.row_stage["com_ferm"]
            self.dico_test_setup(dico_formulaire)
        if type_formulaire == "COM_O":
            dico_formulaire = self.row_stage["com_ouv"]
            self.dico_test_setup(dico_formulaire)
        # affichage repeating panel et maj drop down des textes dispos    
        self.maj_display(dico_formulaire)
        
    def drop_down_textes_formulaire_change(self, **event_args):
        """This method is called when an item is selected"""
        global dico_formulaire
        global dico_test
            
        row = self.drop_down_textes_formulaire.selected_value  # row du texte
        if row is None:
            alert("Vous devez sélectionner un texte !")
            self.drop_down_code_stage.focus()
            return
        else:
            clef = row["code"]  # extraction de la clef à ajouter à partir de la row sélectionnée de la dropbox

        # relecture du fichier formulaire en temp car une question peut avoir été détruite en template 23 
        row_temp=app_tables.temp.search()[0]
        dico_formulaire=row_temp['dico_formulaire']
        
        # rajout clef/valeur ds dico dico_formulaire
        clef = str(len(dico_formulaire)+1)
        obl = ""
        if row["obligation"] is True:
            obl = "obligatoire"
        else:
            obl = "facultative"
        dico_formulaire[clef] = [                          # AJOUT DE LA CLEF DS LE DICO
                                row["text"],
                                obl,
                                row["code"]
                                ]

        # réécriture du dico_test (sert pour fonction display, pour initiliser drop down text formulaire)
        list_keys = []
        dico_test = {}
        list_keys = dico_formulaire.keys()
        for cle in list_keys:  #lecture à partir de la liste des clés
            key_test = dico_formulaire[cle][2]
            dico_test[key_test] = [row["code"]]
          
        if len(dico_test)==10:
            alert(f"Vous avez atteint le maximum de questions {len(dico_test)}/10!\n\nVous pouvez effacer ou mofifier une question !")
            self.drop_down_textes_formulaire.enabled=False   
                
        # affichage repeating panel et maj drop down des textes dispos    
        self.maj_display(dico_formulaire) 
        self.sov_dico(dico_formulaire) 
        
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")

    def maj_display(self,dico_formulaire):   
        
        # affichage du repeating panel des textes dèjà dans le dictionaire lu 
        if dico_formulaire != {}:
            # initialisation sauvegarde du dico_formulaire ds TABLE TEMP au cas où on efface une question dès l'affichage    
            table_temp = app_tables.temp.search()[0]  # sauvegarde du dico ds TABLE TEMP
            table_temp.update(dico_formulaire=dico_formulaire)
            
            # dico lu de la table codes_stages, col du formulaire choisi doit être transformé en liste pour affichage ds le repeat panel
            list_keys = dico_formulaire.keys()
            print('nb de clés: ',len(list_keys))
            #list_keys = sorted(list_keys)  # création de la liste triée des clefs du dictionaire formulaire
            # j'affiche tous les textes du formulaire
            list_repeat_panel = []
            for cle in list_keys:  #lecture à partir de la liste des clés
                #list_repeat_panel.append((cle,dico_formulaire[cle][0])
                list_repeat_panel.append((cle,dico_formulaire[cle][0],dico_formulaire[cle][1],dico_formulaire[cle][2]))
            self.repeating_panel_2.visible = True
            self.repeating_panel_2.items = list(list_repeat_panel)  # liste des clefs (code des formulaires)
            
        # Initialisation drop down textes_formulaire 
        self.dico_test_setup(dico_formulaire)
        type_formulaire = self.drop_down_type_formulaire.selected_value
        list_drop_down = []
        list_textes = app_tables.texte_formulaires.search(tables.order_by("code", ascending=True))
        for row in list_textes:
            cod=row["code"][0:5]
            if cod == type_formulaire:
                # si ce texte n'est pas déjà dans les clés du dico_test ,je l'affiche
                if not dico_test.get(row["code"]):
                    list_drop_down.append((row["text"],row))
        self.drop_down_textes_formulaire.items=list_drop_down       
        self.drop_down_textes_formulaire.visible = True

        # Sauvegarde du dico_formulaire ds la variable text-area _sov_dico
        self.label_sov_dico.text = dico_test
        

    def sov_dico(self, dico_formulaire):
        # modif du dico_formulaire en table codes_stages
        code_stage_row = self.drop_down_code_stage.selected_value
        type_formulaire = self.drop_down_type_formulaire.selected_value
        result = anvil.server.call("modif_dico_formulaire_codes_stages", code_stage_row, dico_formulaire, type_formulaire )
        if not result:
            alert("Erreur: écriture du dictionnaire non effectuée !")
            return
            
        # sauvegarde du dico_formulaire ds TABLE TEMP    
        table_temp = app_tables.temp.search()[0]  # sauvegarde du dico ds TABLE TEMP
        table_temp.update(dico_formulaire=dico_formulaire)   
        
    def dico_test_setup(self, dico_formulaire):    
    # initilisation du dico test à partir du dico formulaire : la cle devient le code du texte pour init drop down textes_formulaire
        # boucle sur le dictionnaire dico_formulaire
        global dico_test
        dico_test = {}
        try:
            for clef, valeur in dico_formulaire.items():
                    key=valeur[2]
                    #alert(f"valeur 0: {clef[0]}\n valeur 1: {clef[1]}")
                    key = valeur[2]          # le code du texte est en position 3 dans le dico enregistré ds la table
                    dico_test[key] = [
                                    valeur[0],
                                    valeur[1]    
                                    ]
        except:
            pass
            
            # initilistaion du dico_formulaire ds TABLE TEMP    
            table_temp = app_tables.temp.search()[0]  # sauvegarde du dico ds TABLE TEMP
            table_temp.update(dico_formulaire={}) 
            
            dico_formulaire={}
            self.sov_dico(dico_formulaire)
            self.drop_down_type_formulaire_change()


        