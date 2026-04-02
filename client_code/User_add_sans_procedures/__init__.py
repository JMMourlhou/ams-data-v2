from ._anvil_designer import User_add_sans_proceduresTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables

from .. import French_zone # POur acquisition de date et heure Francaise (Browser time)
import anvil.tables.query as q    # queries
from ..AlertHTML import AlertHTML # pour affichage des alertes 
from .. import Mail_valideur  # pour test du mail format 

class User_add_sans_procedures(User_add_sans_proceduresTemplate):
    def __init__(self, stage_init=None, pour_stage_init=None, role=None, nom="", prenom="", tel="", mail="" ,**properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.text_box_role.text = role
        self.text_box_nom.text = nom
        self.text_box_prenom.text = prenom
        self.text_box_tel.text = tel
        self.text_box_mail.text = mail
        if nom != "":
            self.button_valid.visible = True

        #==========================================================================================================================================================    
        # sélection des stages si la saisie du formulaire a été validée (saisie_satisf_ok=True) ou (saisie_suivi=ok=True)
        # Permet de ne pas afficher tous les stages
        # Impose d'avoir créé le stage qui contiendra ce user ET d'avoir authorisé le formulaire de suivi ou de satisf
        # sélection des stages visualisés ds dropdown (si la saisie du formulaire a été authorisée (table 'stages': saisie_suivi_ok=True) ou saisie_satisf_ok=True)
        # initialistaion de la drop down codes suivi des stagiaires
        liste1 = app_tables.stages.search(
            tables.order_by("date_debut", ascending=False),
            q.any_of(
                q.any_of(saisie_suivi_ok=True),
                q.any_of(saisie_satisf_ok=True)
            )
        )
        liste_stage_drop_down_stages = []
        for stage in liste1:
            liste_stage_drop_down_stages.append((stage["code"]['code'] +"  #" + str(stage['numero'])+"  du " + str(stage["date_debut"]), stage))
        self.drop_down_code_stages.items = liste_stage_drop_down_stages
        self.drop_down_code_stages.selected_value = None
        
        # pour ne pas répéter la sélection du stage (voir fin du BT validation)
        if stage_init is not None:
            self.drop_down_code_stages.selected_value = stage_init
            # initilisation du drop down du stage du tuteur
            self.init_stage_tuteur()
            self.drop_down_tuteur_pour_quel_stage.selected_value = pour_stage_init
            self.column_panel_stage_de_travail_du_tuteur.visible = True
            self.text_box_role.text = role
        
        
    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_add.visible = True

    def text_box_mail_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        # Mail format validation
        mail = self.text_box_mail.text.lower()
        result = Mail_valideur.is_valid_email(mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            AlertHTML.error("Adresse mail :", "L'adresse mail contient une erreur !")
            self.text_box_mail.focus()
            return
        self.button_valid.visible = True
        
    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        if len(self.text_box_nom.text) < 3:
            alert("Le nom n'est pas assez long !")
            self.text_box_nom.focus()
            return
        """
        if len(self.text_box_prenom.text) < 3:
            alert("Le prénom n'est pas assez long !")
            self.text_box_prenom.focus()
            return
        """
        test_role = ["S","s","F","f","T","t","B","b","A","a","V","v"] # je n'accepte que ces lettres, minuscules acceptées car upper ensuite
        if self.text_box_role.text not in test_role:
            alert("Le role doit être soit: S, F, T, B, A, V !")
            self.text_box_role.focus()
            return
            
        # Mail format validation
        self.mail = self.text_box_mail.text.lower()
        result = Mail_valideur.is_valid_email(self.mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            alert("Le mail n'a pas le bon format !")
            self.text_box_mail.focus()
            return
        
        result = anvil.server.call("new_user",
                                   self.text_box_nom.text.capitalize(),
                                   self.text_box_prenom.text.capitalize(),
                                   self.text_box_tel.text,
                                   self.text_box_mail.text.lower(),
                                   self.text_box_role.text.upper(),
                                   signed_up = French_zone.french_zone_time(),  # importé en ht de ce script
                                   temp=self.drop_down_code_stages.selected_value["numero"],
                                   temp_for_stage = self.drop_down_tuteur_pour_quel_stage.selected_value["numero"]
                                  )
        if result is not None:
            alert(result)  # user existant
        else:
            alert("Création effectuée !")
        #                                    Stage du tuteur                            Pour quel stage                                        role du nouveau user 
        open_form('User_add_sans_procedures',self.drop_down_code_stages.selected_value, self.drop_down_tuteur_pour_quel_stage.selected_value, self.text_box_role.text) # pour ne pas à avoir à resélectionner le stage

    def drop_down_code_stages_change(self, **event_args):
        """This method is called when an item is selected"""
        stage_row = self.drop_down_code_stages.selected_value
        self.text_box_role.text = stage_row["type_stage"]
        # si c'est un stage tuteur, je demande sur quel stage il est tuteur
        if stage_row["type_stage"] == "T":
            self.column_panel_stage_de_travail_du_tuteur.visible = True
        # initilisation du drop down du stage du tuteur
        self.init_stage_tuteur()
            
    def init_stage_tuteur(self, **event_args):
        #==========================================================================================================================================================
        # initialistaion de la drop down stage du tuteur
        liste1 = app_tables.stages.search(
            tables.order_by("date_debut", ascending=False),
            q.all_of(
                # ET
                q.any_of(q.any_of(code_txt="BPAAN"), q.any_of(code_txt="BPMOTO")), # BPAAN ou BPMOTON
                #q.any_of(q.any_of(saisie_satisf_ok=True), q.any_of(saisie_suivi_ok=True)), # saisie_satisf_ok=True  ou saisie_suivi_ok=True
            )
        )
        
        liste_stages = []
        for stage in liste1:
            liste_stages.append((stage["code"]['code'] + "  #" + str(stage['numero']) + "  du " + str(stage["date_debut"]), stage))
        self.drop_down_tuteur_pour_quel_stage.items = liste_stages
        #==========================================================================================================================================================

    def text_box_nom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

  


    
    
