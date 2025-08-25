from ._anvil_designer import ItemTemplate11Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....import French_zone # pour calcul tps traitement
from ....import Pre_R_doc_name        # Pour générer un nouveau nom au document chargé
from ....Pre_Visu_img_Pdf import Pre_Visu_img_Pdf   #pour afficher un document avant de le télécharger


class ItemTemplate11(ItemTemplate11Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.                              Bt docs requis cliqué
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.test_img_just_loaded = False
        
        self.email = self.item['stagiaire_email']
        self.item_requis = self.item['item_requis']
        self.stage_num = self.item['stage_num']
        #txt2 = self.item['item_requis']['code_pre_requis']
        txt2 = self.item['code_txt']
        #txt1 = self.item['item_requis']['requis']
        txt1 = self.item['requis_txt']
        self.label_1.text = txt1 +" / "+ txt2
        
        if self.item['doc1'] is not None:
            self.image_1.source = self.item['doc1']              # DIPLAY L'image basse qualité 
            self.button_del.visible = True
            self.button_visu.visible = True
            self.file_loader_1.visible = False
            self.button_rotation.visible = True
        else:
            self.button_del.visible = False
            self.button_visu.visible = False
            self.file_loader_1.visible = True
            self.button_rotation.visible = False

    def button_visu_click(self, **event_args):
        """This method is called when the button is clicked"""
        # nouveau nom doc
        new_file_name = Pre_R_doc_name.doc_name_creation(self.stage_num, self.item_requis, self.email)   # extension non incluse
        open_form('Pre_Visu_img_Pdf', self.item['doc1'], new_file_name, self.stage_num, self.email, self.item_requis, origine="admin")
    
    def file_loader_1_change(self, file, **event_args):
        if file is not None:  #pas d'annulation en ouvrant choix de fichier
            start = French_zone.french_zone_time()

            # Type du fichier loaded ?
            path_parent, file_name, file_extension = anvil.server.call('path_info', str(file.name))
            list_extensions = [".jpg", ".jpeg", ".bmp", ".gif", ".jif", ".png"]
            if file_extension in list_extensions:   

                # on sauve par uplink le file media image
                self.image_1.source = file
                result = anvil.server.call('pre_requis',self.item, file)  # appel uplink fonction pre_requis sur Pi5
                print(result)

            if file_extension == ".pdf":      
                # génération du JPG à partir du pdf bg task en bg task
                self.task_pdf = anvil.server.call('pdf_into_jpg_bgtasked', file, self.item['stage_num'], self.item['stagiaire_email'])    
                self.timer_2.interval=0.05

        # gestion des boutons        
        self.file_loader_1.visible = False
        self.button_rotation.visible = True
        self.button_visu.visible = True  
        self.button_del.visible = True 

        end = French_zone.french_zone_time()
        temps = f"Temps de traitement image: {end-start}"
        print(temps)

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        result = anvil.server.call('pr_stagiaire_del',self.email, self.stage_num, self.item_requis )
        if result:
            self.image_1.source = None
            self.button_visu.visible = False
            self.button_del.visible = False
            self.button_rotation.visible = False
            
            self.file_loader_1.text = ""
            self.file_loader_1.font_size = 18
            self.file_loader_1.visible = True
        else:
            alert("Pré Requis non enlevé")


    def timer_2_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.task_pdf.is_completed(): # lecture de l'image sauvée en BG task
            # lecture de la liste sauvée par bg task ds row du stagiaire_inscrit
            self.timer_2.interval=0
            anvil.server.call('task_killer',self.task_pdf)

            row = app_tables.stagiaires_inscrits.get(q.fetch_only("temp_pr_pdf_img"),
                                                     stage=self.item['stage_num'],
                                                     user_email=self.item['stagiaire_email']
                                                    )
            if row:
                # Venant d'une table et non d'un file loader, file est un lazy BlobMedia
                file=row['temp_pr_pdf_img']

                """  ---------------------------------------------------------------------------------------------------------------------------------------------
                TRANSFORMATION D'UN LAZY MEDIA (img qui vient d'une table) EN BLOB MEDIA (En sortie du file loader et transformable en SERVER side pour resize...)
                """
                media_object = anvil.URLMedia(file.url)
                # -----------------------------------------------------------------------------------------------------------------------------------------------
                # on sauve par uplink le file media image
                self.image_1.source = file
                result = anvil.server.call('pre_requis',self.item, media_object)  # appel uplink fonction pre_requis sur Pi5
                print(result)
            else:
                alert('timer_2_tick: row stagiaire inscrit non trouvée')

    def button_rotation_click(self, **event_args):
        """This method is called when the button is clicked"""
        # pour calcul du temps de traitement
        row = app_tables.pre_requis_stagiaire.get(
            stage_num=self.stage_num,
            item_requis=self.item_requis,
            stagiaire_email=self.email
        )
        file=row["doc1"]
        media_object1 = anvil.URLMedia(file.url)
        media_object2 = anvil.image.rotate(media_object1,90)
        # -----------------------------------------------------------------------------------------------------------------------------------------------
        # on sauve par uplink le file media image
        self.image_1.source = file
        result = anvil.server.call('pre_requis',self.item, media_object2)  # appel uplink fonction pre_requis sur Pi5
        print(result)

        #relecture pour affichage du thumb rotated
        row = app_tables.pre_requis_stagiaire.get(
            stage_num=self.stage_num,
            item_requis=self.item_requis,
            stagiaire_email=self.email
        )
        self.image_1.source = row['doc1']

                
