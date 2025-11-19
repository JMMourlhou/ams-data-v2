from ._anvil_designer import ItemTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media
from ...import Pre_R_doc_name        # Pour générer un nouveau nom au document chargé
from ...import French_zone # pour calcul tps traitement

class ItemTemplate3(ItemTemplate3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.test_img_just_loaded = False  # pour savoir si l'image vient d'être chargée (voir visu image)
        self.text_box_1.text = self.item['requis_txt']
        
        if self.item['doc1'] is not None:    # Si doc existant
            self.image_1.source = self.item['doc1']
            self.button_del.visible = True
            self.button_visu.visible = True
            self.file_loader_1.visible = False
        else:                                 # si doc none
            self.image_1.source = None       # permet de tester le click sur l'image
            self.button_del.visible = False 
            self.button_visu.visible = False
            self.button_rotation.visible = False
            
        self.stage_num =   self.item['stage_num']        # Row stage
        self.item_requis = self.item['item_requis']      # Row Item requis
        self.email =       self.item['stagiaire_email']  # Row user

    def file_loader_1_change(self, file, **event_args):
        if file is not None:  #pas d'annulation en ouvrant choix de fichier
            start = French_zone.french_zone_time()
        
            # Type du fichier loaded ?
            path_parent, file_name, file_extension = anvil.server.call('path_info', str(file.name))
            list_extensions_img = [".jpg", ".jpeg", ".bmp", ".gif", ".jif", ".png"]
            list_possible = [".jpg", ".jpeg", ".bmp", ".gif", ".jif", ".png", "pdf"]
            if file_extension in list_extensions_img:   # Fichier image choisit
                # on sauve par uplink le file media image
                self.image_1.source = file
                result = anvil.server.call('pre_requis',self.item, file)  # appel uplink fonction pre_requis sur Pi5
                # gestion des boutons        
                self.file_loader_1.visible = False
                self.button_rotation.visible = True
                self.button_visu.visible = True  
                self.button_del.visible = True 
                end = French_zone.french_zone_time()
                temps = f"Temps de traitement image: {end-start}"
                #print(temps)
            elif file_extension == ".pdf":      
                self.traitement_pdf(file)
            else:  # erreur: le format choisit n'est pas un fichierimage ou pdf
                alert(f"le type de fichier doit être un de ces types : {list_possible}")
        
    def button_visu_click(self, **event_args):
        """This method is called when the button is clicked"""
        # nouveau nom doc
        new_file_name = Pre_R_doc_name.doc_name_creation(self.stage_num, self.item_requis, self.email)   # extension non incluse
        open_form('Pre_Visu_img_Pdf', self.item['doc1'], new_file_name, self.stage_num, self.email, self.item_requis, origine="admin")

    def button_del_click(self,  **event_args):
        """This method is called when the button is clicked"""
        result = anvil.server.call('pr_stagiaire_del',self.email, self.stage_num, self.item_requis )
        if result:
            self.image_1.source = None
            self.button_visu.visible = False
            self.button_del.visible = False
            self.button_rotation.visible = False
            
            self.file_loader_1.text = "Choisir"
            self.file_loader_1.font_size = 14
            self.file_loader_1.visible = True
        else:
            alert("Pré Requis non enlevé")

    

    def button_rotation_click(self, **event_args):
        """This method is called when the button is clicked"""
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
        #print(result)
        
        #relecture pour affichage de doc1 rotated
        row = app_tables.pre_requis_stagiaire.get(
                                                        stage_num=self.stage_num,
                                                        item_requis=self.item_requis,
                                                        stagiaire_email=self.email
                                                    )
        self.image_1.source = row['doc1']

    def image_1_mouse_down(self, x, y, button, keys, **event_args):
        """This method is called when a mouse button is pressed on this component"""
        if self.image_1.source is not None:        # non Vide
            self.button_visu_click()

    def button_scan_click(self, **event_args):
        """This method is called when the button is clicked"""
        # envoi vers pi5 par uplink du media, stage_num, item_requis, stagiaire_email
        # module python sur Pi5, répertoire /mnt/ssd-prog/home/jmm/AMS_data/uplinks/scan_image/scan.py
        media = self.item['doc1']
        row_id = self.item.get_id()  # row ds table Pre_Requis_stagiaire pour sauver l'image traitée
        try:
            self.image_scanned.source = anvil.server.call('scan_media', media, row_id)
        except Exception as e:
            alert(f"Erreur pendant le scan: {e}")

    def traitement_pdf(self, lazy_media, **event_args):   
        start = French_zone.french_zone_time()
        """
        Une colonne de type Media dans une table Anvil stocke souvent un LazyMedia, qui n’est pas un vrai fichier,
        c’est un pointeur vers un blob stocké sur le serveur Anvil,
        il n’est téléchargé que sur demande, quand j'appelle .get_bytes() ou que tu le transmets au client.
        Si je passes ce LazyMedia à une fonction Python qui attend un vrai fichier, PyPDF2, Pillow, pdf2image, etc., Anvil ne sait pas rendre le contenu → erreur Invalid (Lazy) Media object.
        Je dois donc le transformer:
        """
        # Materialiser le LazyMedia
        pdf_bytes = lazy_media.get_bytes()

        new_file = anvil.BlobMedia(
            "application/pdf",
            pdf_bytes,
            name=lazy_media.name or "diplome.pdf"
        )

        # Je peux maintenant l'envoyer pour traitement en UPLINK:
        # ======================================================================================================== CREATION DU DICO
        # acquisition du PR_row
        try:
            pr_row = app_tables.pre_requis.get(code_pre_requis=self.item['item_requis']['code_pre_requis'])
        except Exception as e:
            alert(f"PR_row non trouvé en table 'pre_requis': {e}")
            return

        result={}        
        cle = 1
        value = ( 
            self.item['stage_num'] ,        # stage row
            self.item['stagiaire_email'],   # student row
            pr_row                          # pr_row
        )
        result[str(cle)]=value    # clé doit être type str qd on envoi en server side

        # vérification : nb de pages du pdf = nb de clés du dico result
        for clef,val in result.items():
            print(f"{clef}")
            print(f"stage row: {val[0]}")
            print(f"student row: {val[1]}")
            print(f"pr_row: {val[2]}")
            print()
        #                                                                          Fin de Création du dico
        # =========================================================================================================================================

        # ENVOI EN UPLINK sur Pi5                          pdf file,  dico
        nb_pages = anvil.server.call("pre_requis_from_pdf", new_file, result, 'unik')  # unik indique qu'il n'y aura que la 1er page à prendre même s'ily a plusieurs pages
        print(f"{nb_pages} document sauvé !")

        # on affiche le doc:
        try:
            row_pr = app_tables.pre_requis_stagiaire.get(
                stage_num=self.item['stage_num'],
                stagiaire_email=self.item['stagiaire_email'],
                item_requis=self.item['item_requis']
            )
        except Exception as e:
            alert(f"Erreur en relecture du row_pr :{e}")
            return
        self.image_1.source = row_pr['doc1']
        # gestion des boutons        
        self.file_loader_1.visible = False
        self.button_rotation.visible = True
        self.button_visu.visible = True  
        self.button_del.visible = True 

        end = French_zone.french_zone_time()
        temps = f"Temps de traitement image: {end-start}"
        print(temps)

           
        
        

            

            