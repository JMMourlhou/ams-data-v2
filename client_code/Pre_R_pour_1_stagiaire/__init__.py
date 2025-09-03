from ._anvil_designer import Pre_R_pour_1_stagiaireTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

global code_stage
code_stage = ""
global dico_pre_requis     # dico de tous les pr existants
dico_pre_requis = {}
global dico_pre_requis_stg  # dico des pr pour ce stgiaire
dico_pre_requis_stg = {}

class Pre_R_pour_1_stagiaire(Pre_R_pour_1_stagiaireTemplate):
    def __init__(self,stagiaire_inscrit_row, re_display=False, **properties):  # row stagiaire inscrit, vient de pré_requis_pour stagiaire admin
        # Set Form properties and Data Bindings.
       
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()   # récupération de la forme mère pour revenir ds la forme appelante
        
        #import anvil.js    # pour screen size
        from anvil.js import window # to gain access to the window object
        global screen_size
        screen_size = window.innerWidth
        
        self.stagiaire_inscrit_row = stagiaire_inscrit_row
        self.stagiaire_email = stagiaire_inscrit_row['user_email']
        self.stage = stagiaire_inscrit_row['stage']
        nom = stagiaire_inscrit_row['name'].capitalize()
        if screen_size < 800:
            pr = stagiaire_inscrit_row['prenom'][0].capitalize()   # 1ere lettre du prénom
            self.label_3.text = "Pré-R perso pour "+nom+" "+pr+"  / "+stagiaire_inscrit_row['stage_txt']
        else:
            pr = stagiaire_inscrit_row['prenom'].capitalize()
            self.label_3.text = "Pré-Requis personnalisés pour "+nom+" "+pr+"  / "+stagiaire_inscrit_row['stage_txt']

        # search de tous les pré-requis existants
        self.liste_tous_pr = app_tables.pre_requis.search(tables.order_by("requis", ascending=True),
                                                    q.fetch_only("requis","code_pre_requis")
                                                    )

        self.display()

    def drop_down_pre_requis_change(self, **event_args):
        """This method is called when an item is selected"""
        row = self.drop_down_pre_requis.selected_value  # row du pre_requis
        if row is None:
            alert("Vous devez sélectionner un pré-requis !")
            self.drop_down_code_stage.focus()
            return
        # Ajout ds table pre-requis-stagiaire
        result = anvil.server.call(
                            "add_1_pre_requis",
                            self.stage,
                            self.stagiaire_email,
                            row,
                        )
        print("ajout: ", result)
       
        # réaffichage des pré requis par reinitialisation 
        self.display()                        

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Je connais la forme appelante: en init : self.f = get_open_form()
        try:
            self.f.button_maj_pr.visible = True
            self.f.button_gestion_pre_requis.visible = True
            self.f.column_panel_pr_par_personne.visible = False
            self.f.drop_down_code_stage.selected_value = None
            self.f.drop_down_personnes.selected_value = None
        except:
            pass
        open_form(self.f)

    # Affichage qui permet de ne pas réinitialiser la forme et donc de garder self.f = get_open_form() 
    def display(self):
        liste_drop_d = []
        global dico_pre_requis
        dico_pre_requis = {}

        # liste des pré-requis existants du stagiaire
        self.liste_pr_stagiaire = app_tables.pre_requis_stagiaire.search( q.fetch_only("requis_txt",
                                                                       stagiaire_email=q.fetch_only("email"),
                                                                       ),
                                                                        numero=int(self.stagiaire_inscrit_row['numero']),
                                                                        stagiaire_email=self.stagiaire_inscrit_row["user_email"]
                                                                         )
        # Création du dict des pr du stagiaire
        global dico_pre_requis_stg  # dico des pr pour ce stgiaire
        dico_pre_requis_stg = {}
        for pr_st in self.liste_pr_stagiaire:
            clef = pr_st['requis_txt']
            valeur = ""
            dico_pre_requis_stg[clef] = valeur
            print(dico_pre_requis_stg.keys())

        
        for pr in self.liste_tous_pr:
            clef_search = dico_pre_requis_stg.get(pr['requis'])
            if clef_search is None:
                liste_drop_d.append((pr['requis'], pr))
                dico_pre_requis[pr['code_pre_requis']] = pr['requis']
                
        # Re_initialisation drop D Pré-requis à ajouter
        self.drop_down_pre_requis.items = liste_drop_d
        # affichage des pré-requis du stagiaire
        self.repeating_panel_1.items = self.liste_pr_stagiaire
        
