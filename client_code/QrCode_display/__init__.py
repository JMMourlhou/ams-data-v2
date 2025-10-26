from ._anvil_designer import QrCode_displayTemplate
from anvil import *

import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import French_zone
from anvil import open_form 

class QrCode_display(QrCode_displayTemplate):
    def __init__(self, log_in=False, num_stage=0, **properties):
        # log_in True qd on veut log in sur l'app sans rien d'autre 
        
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens
        self.f = get_open_form()  # form appelante
        if log_in is True:
            # si log_in =True, appel du qr_code pour que les stagiaires log in ds l'appli, donc pas de num stage
            self.label_titre.text = "Flashez pour vous connecter à l'appli AMSdata "

        # si log_in = False, appel du qr_code pour que les stagiaires s'inscrivent au stage
        if log_in is False:
            if num_stage==0 :
                alert("Numéro de stage non valide")
                return
            
            # lecture du stage par son numéro 
            stage = app_tables.stages.get(numero=int(num_stage)) 
            if not stage:
                alert("Code du stage non trouvé")
                return
            txt_stage=stage['code']['code']
            txt_stage=txt_stage.replace("_","")

            # si num_stage="1003", stage tuteur, il faut savoir pour quel stage lestuteurs seront inscrits
            # l'info sera contenue ds temp_pour_stage ds la table user puis ds table stagiaire inscrit)
            if int(num_stage) == 1003:
                # Initialisation du Drop down num_stages et dates
                list = app_tables.stages.search(
                                                tables.order_by("code_txt", ascending=True),
                                                numero = q.less_than(900)
                                                )
                self.drop_down_num_stages.items = [(r['code_txt']+" / "+str(r['date_debut'])+" / "+str(r['numero']), r) for r in list]
                self.column_panel_choix_stage.visible = True
                self.text_area_lien.visible = False
                self.label_titre.text = "Choisir quel stage encadre le tuteur"
            else:
                self.label_titre.text = "Flashez pour s'inscrire au "+ txt_stage + " du " + str(stage['date_debut'].strftime("%d/%m/%Y"))
                self.link_creation(num_stage, 0)        

    def recup_time(self, **event_args): 
        time=French_zone.french_zone_time()
        time_str=""
        time_str=str(time)
        time_str=time_str.replace(" ","_")
        return(time_str)

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)

    # si stage 1003 pour tuteurs 
    def drop_down_num_stages_change(self, **event_args):
        """This method is called when an item is selected"""
        pour_stage_row = self.drop_down_num_stages.selected_value
        pour_stage_num = pour_stage_row['numero']
        self.text_area_lien.visible = False
        self.label_titre.text = "Flashez pour inscrire les tuteurs du stage "+ pour_stage_row['code_txt'] + " du " + str(pour_stage_row['date_debut'].strftime("%d/%m/%Y"))
        self.link_creation(1003, pour_stage_num)
    
    def link_creation(self, num_stage, pour_stage=0):
        # Lecture de la variable globale "code_app1" ds table variables_globales
        app = anvil.server.call('get_variable_value', "code_app1")
        # param 
        time = self.recup_time()
        param="/#?a=qrcode" + "&stage=" + str(num_stage) +  "&pour=" +  str(pour_stage)  + "&t=" + time
        #param="/#?a=qrcode" + "&stage=" + str(num_stage) + "&t=" + time

        stage_link = app + param  # App "AMS Data"  + code stage
        
        self.text_area_lien.text = stage_link  # affichage du lien
        self.text_area_lien.visible = True
        
        media=anvil.server.call('mk_qr_code',stage_link) # affichage du QR code
        self.image_1.source=media

        
        

        


