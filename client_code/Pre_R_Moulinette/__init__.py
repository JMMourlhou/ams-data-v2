from ._anvil_designer import Pre_R_MoulinetteTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# boucle sur les images dela table pré-requis pour resize jpg en 1000 x 800   ou 800 x 1000
class Pre_R_Moulinette(Pre_R_MoulinetteTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def button_go_click(self, **event_args):
        """This method is called when the button is clicked"""
        # BOUCLE SUR LA TABLE entierre
        self.liste = app_tables.pre_requis_stagiaire.search(
                                                            tables.order_by('numero', ascending=False),
                                                           )
        #print(len(self.liste))
        
        self.cpt = 1
        for row in self.liste:            
            #print(self.cpt)
            #test = str(row['doc1'])
            test = row['doc1']
            #print(test)
            if  row['doc1'] is not None:
                self.cpt += 1
                file = row['doc1']
                 # Type de fichier ?
                path_parent, file_name, file_extension = anvil.server.call('path_info', str(file.name))
                #print("file_name1: ",file_name)
                #print("file_extension: ",file_extension)
                
                # création d'une liste, à partir du séparateur "."
                liste_nom_fichier = file_name.split('.')
                suffix = liste_nom_fichier[0]
                file_name = suffix+".jpg"
                #print("file_name: ",file_name)
                
                
                self.task_img, self.durée_traitement = anvil.server.call('run_bg_task_resize_jpg', row, file_name)    
                self.timer_1.interval=0.5
           


    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.task_img.is_completed(): # lecture de l'image sauvée en BG task
            print(f"{self.cpt-1} lignes traitées")
            self.timer_1.interval=0
            anvil.server.call('task_killer',self.task_img, self.durée_traitement)
