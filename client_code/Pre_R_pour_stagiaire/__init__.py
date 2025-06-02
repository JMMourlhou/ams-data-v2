from ._anvil_designer import Pre_R_pour_stagiaireTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
global user_pr
user_pr = anvil.users.get_user()

class Pre_R_pour_stagiaire(Pre_R_pour_stagiaireTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        global user_pr
        if user_pr:
            self.label_1.text = "Documents à fournir pour " + user_pr['prenom'] + " " + user_pr['nom']
            # Drop down stages inscrits du user
            liste0 = app_tables.stagiaires_inscrits.search(q.fetch_only("user_email","stage"),           # <----------------------  A Modifier? 
                                                            user_email=user_pr)
            #print("nb; ", len(liste0))
            liste_drop_d = []
            for row in liste0:
                #lecture fichier père stage
                stage=app_tables.stages.get(q.fetch_only("date_debut"),
                                                            numero=row['stage']['numero']
                                            )
                
                #lecture fichier père type de stage
                type=app_tables.codes_stages.get(q.fetch_only("code"),
                                                    code=stage['code']['code']
                                                )
                
                if stage['type_stage']=="S":    # Si stagiaire, j'affiche la date du stage
                    liste_drop_d.append((type['code']+"  du "+str(stage['date_debut']), row))
                else:
                    liste_drop_d.append((type['intitulé'], row))
                    
            #print(liste_drop_d)
            self.drop_down_code_stage.items = liste_drop_d

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def drop_down_code_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        row_stagiaire_inscrit = self.drop_down_code_stage.selected_value   # Stage sélectionné du user ds drop_down (row table stagiaire inscrit)
        if row_stagiaire_inscrit is not None:
            # lecture fichier père stages
            row_stage = app_tables.stages.get(numero=row_stagiaire_inscrit['stage']['numero'])
            # lecture des pré requis pour ce stage et pour ce stagiaire
            global user_pr
            liste_pr = app_tables.pre_requis_stagiaire.search(q.fetch_only("item_requis","thumb"),
                                                            stagiaire_email=user_pr,
                                                            stage_num=row_stage
                                                            )
            self.repeating_panel_1.items = liste_pr
        
