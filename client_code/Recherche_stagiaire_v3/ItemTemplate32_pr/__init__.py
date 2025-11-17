from ._anvil_designer import ItemTemplate32_prTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import time
from ... import French_zone # calcul tps traitement
from ... import Pre_R_doc_name

class ItemTemplate32_pr(ItemTemplate32_prTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        """
        items:
                "clef":                 (requis_txt + numero de stage)
                "item_requis":       row du PR
                "type_stage_txt":    PSC, PSE1, ... 
                "stagiaire_email":   stagiaire user_row
                "stage_row":         row du stage 
                "doc1":              img 
                "date_stage":        date du stage
                "requis_txt":        intitulé en clair du PR
        """
        # Any code you write here will run before the form opens.
        self.test_img_just_loaded = False

        #self.email = self.item['stagiaire_email']
        self.stagiaire_row = self.item['stagiaire_email']
        self.stage_num = self.item['stage_row']                # =================================

        txt2 = self.item['type_stage_txt']
        txt1 = self.item['requis_txt']
        self.label_1.text = txt1 +" / "+ txt2

        if self.item['doc1'] is not None:
            self.image_1.source = self.item['doc1']           
            self.button_del.visible = True
            self.button_visu.visible = True
            self.file_loader_1.visible = False
            self.button_del_pour_ce_stagiaire.visible = False
            self.button_rotation.visible = True
        else:
            self.image_1.source = None       # permet de tester le click sur l'image
            self.button_del.visible = False
            self.button_visu.visible = False
            self.file_loader_1.visible = True
            self.button_del_pour_ce_stagiaire.visible = True
            self.button_rotation.visible = False
            
        #print(f"<{self.item['item_requis']['code_pre_requis'][0:6].strip()}>")
        #print(f"<{self.item['item_requis']['code_pre_requis'].strip()}>")
        # si on recherche un diplome ou une attestation
        if self.item['item_requis']['code_pre_requis'].strip() in ("DIP-BNSSA", "DIP-PSE1", "DIP-PSE2", "DIP-PSC") or self.item['item_requis']['code_pre_requis'][0:6].startswith("ATT-FC"): 
            self.button_search.visible = True
        else:
            self.button_search.visible = False

            
    def button_visu_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Relecture du row de la table pre_requis_stagiaire: (self.item nest pas le row du pre requis)
        try:
            row = app_tables.pre_requis_stagiaire.get(
                stage_num=self.item['stage_row'],
                stagiaire_email=self.item['stagiaire_email'],
                item_requis=self.item['item_requis']
            )
            #alert(f"ok: {row['requis_txt']} pour {row['nom']} {row['prenom']}")
        except Exception as e:
            alert(f"Erreur de relecture du row pre_requis_stagiaire: {e}")
            return
        # nouveau nom doc
        new_file_name = Pre_R_doc_name.doc_name_creation(row['stage_num'], row['requis_txt'], row['stagiaire_email'])   # extension non incluse
        open_form('Pre_Visu_img_Pdf', row['doc1'], new_file_name, self.stage_num, row['stagiaire_email'], row['item_requis'], origine="admin")

    def file_loader_1_change(self, file, **event_args):
        if file is not None:  #pas d'annulation en ouvrant choix de fichier
            if file is not None:  #pas d'annulation en ouvrant choix de fichier
                start = French_zone.french_zone_time()

            # Type du fichier loaded ?
            path_parent, file_name, file_extension = anvil.server.call('path_info', str(file.name))
            list_extensions_img = [".jpg", ".jpeg", ".bmp", ".gif", ".jif", ".png"]
            list_possible = [".jpg", ".jpeg", ".bmp", ".gif", ".jif", ".png", "pdf"]
            if file_extension in list_extensions_img:   # Fichier image choisit
                # on sauve par uplink le file media image
                self.image_1.source = file
                # Relecture du row de la table pre_requis_stagiaire: (self.item nest pas le row du pre requis)
                try:
                    row = app_tables.pre_requis_stagiaire.get(
                        stage_num=self.item['stage_row'],
                        stagiaire_email=self.item['stagiaire_email'],
                        item_requis=self.item['item_requis']
                    )
                    #alert(f"ok: {row['requis_txt']} pour {row['nom']} {row['prenom']}")
                except Exception as e:
                    alert(f"Erreur de relecture du row pre_requis_stagiaire: {e}")
                    return
                result = anvil.server.call('pre_requis',row, file)  # appel uplink fonction pre_requis sur Pi5
                print(result)
                # gestion des boutons        
                self.file_loader_1.visible = False
                self.button_rotation.visible = True
                self.button_visu.visible = True  
                self.button_del.visible = True 
            elif file_extension == ".pdf":      
                MAX_PAGES = 50  # limite maximale de pages, pour empêcher un pdf trop gros, ce qui planterait la mémoire du Pi5
                # Appelle la fonction serveur pour vérifier le nombre de pages
                result = anvil.server.call('get_pdf_page_count', file)   # result est nb pages du pdf ou msg d'erreur
                #alert(f"nb de pages du pdf: {result}")
                if isinstance(result, int) and result > MAX_PAGES:
                    alert("Le PDF est trop grand.")
                elif result == "Le fichier n'est pas un PDF valide.":
                    alert(result)
                else:
                    
                    
                    # génération du JPG à partir du pdf bg task en bg task           stage
                    self.task_pdf = anvil.server.call('process_pdf', file, self.item['stage_row'], self.item['stagiaire_email'])    # on extrait la 1ere page
                    #self.task_pdf = anvil.server.call('process_pdf_background', file, self.item['stage_row'], self.item['stagiaire_email'])    # on extrait la 1ere page
                    self.timer_1.interval=0.05   # le fichier jpg généré est extrait de la colonne temporaire de table stagiaire inscrit en fin de bg task (voir timer_2_tick)
                    # gestion des boutons        
                    self.file_loader_1.visible = False
                    self.button_rotation.visible = True
                    self.button_visu.visible = True  
                    self.button_del.visible = True 

                    end = French_zone.french_zone_time()
                    temps = f"Temps de traitement image: {end-start}"
                    print(temps)
                    
            else:  # erreur: le format choisit n'est pas un fichierimage ou pdf
                alert(f"le type de fichier doit être un de ces types : {list_possible}")

    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""

        # Relecture du row de la table pre_requis_stagiaire: (self.item nest pas le row du pre requis)
        try:
            row = app_tables.pre_requis_stagiaire.get(
                stage_num=self.item['stage_row'],
                stagiaire_email=self.item['stagiaire_email'],
                item_requis=self.item['item_requis']
            )
            #alert(f"ok: {row['requis_txt']} pour {row['nom']} {row['prenom']}")
        except Exception as e:
            alert(f"Erreur de relecture du row pre_requis_stagiaire: {e}")
            return

        result = anvil.server.call('pr_stagiaire_del',row['stagiaire_email'], row['stage_num'], self.item['item_requis'] )
        if result:
            self.image_1.source = None
            self.button_visu.visible = False
            self.button_del.visible = False
            self.button_rotation.visible = False

            self.file_loader_1.text = ""
            self.file_loader_1.font_size = 18
            self.file_loader_1.visible = True
            self.button_del_pour_ce_stagiaire.visible = True
        else:
            alert("Pré Requis non enlevé")


    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.task_pdf.is_completed(): # lecture de l'image sauvée en BG task
            # lecture de la liste sauvée par bg task ds row du stagiaire_inscrit
            self.timer_1.interval=0
            anvil.server.call('task_killer',self.task_pdf)

            row = app_tables.stagiaires_inscrits.get(q.fetch_only("temp_pr_pdf_img"),
                                                     stage=self.item['stage_row'],
                                                     user_email=self.item['stagiaire_email']
                                                    )
            if row:
                # Venant d'une table et non d'un file loader, file est un lazy BlobMedia
                file=row['temp_pr_pdf_img']
                alert("Fichier temp lu de la table stagiaire inscrit")
                file = row['temp_pr_pdf_img']   # LazyMedia
                file = anvil.BlobMedia("image/jpeg", file.get_bytes(), name=file.name)
                # on sauve par uplink le file media image
                try:
                    row_pr = app_tables.pre_requis_stagiaire.get(
                        stage_num=self.item['stage_row'],
                        stagiaire_email=self.item['stagiaire_email'],
                        item_requis=self.item['item_requis']
                    )
                except Exception as e:
                    alert(f"Erreur en relecture du row_pr :{e}")
                    return
                self.image_1.source = file
                result = anvil.server.call('pre_requis',row_pr, file)  # appel uplink fonction pre_requis sur Pi5
                print(result)
            else:
                alert('timer_1_tick: row stagiaire inscrit non trouvé')

    def button_rotation_click(self, **event_args):
        """This method is called when the button is clicked"""

        row = app_tables.pre_requis_stagiaire.get(
            stage_num=self.stage_num,
            item_requis=self.item['item_requis'],
            stagiaire_email=self.stagiaire_row
        )
        if row:
            file=row["doc1"]
            media_object1 = anvil.URLMedia(file.url)
            media_object2 = anvil.image.rotate(media_object1,90)

            # -----------------------------------------------------------------------------------------------------------------------------------------------
            # on sauve par uplink le file media image
            result = anvil.server.call('pre_requis',row, media_object2)  # appel uplink fonction pre_requis sur Pi5
            print(result)
        else:
            alert("Image non retrouvée !")

        #relecture pour affichage du thumb rotated
        row = app_tables.pre_requis_stagiaire.get(
            stage_num=self.stage_num,
            item_requis=self.item['item_requis'],
            stagiaire_email=self.stagiaire_row
        )
        self.image_1.source = row['doc1']

    def image_1_mouse_down(self, x, y, button, keys, **event_args):
        """This method is called when a mouse button is pressed on this component"""
        if self.image_1.source is not None:        # non Vide
            self.button_visu_click()

    def button_del_pour_ce_stagiaire_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.item['doc1'] is not None:
            r=alert("Ce pré-requis n'est pas vide, Voulez-vous vraiment le détruire ?",dismissible=False,buttons=[("oui",True),("non",False)])
        else:
            r=alert(f"Voulez-vous enlever ce pré-requis ({self.item['requis_txt']}) pour {self.stagiaire_row['prenom']} {self.stagiaire_row['nom']}?", dismissible=False ,buttons=[("oui",True),("non",False)])
        if r :   # Oui               
            result = anvil.server.call('pr_stagiaire_del',self.item['stagiaire_email'], self.item['stage_row'], self.item['item_requis'], "destruction" )  # mode  destruction de PR pour ce stgiaire
            if not result:
                alert("Pré Requis non enlevé pour ce stagiaire")
            else:
                alert("Pré Requis enlevé pour ce stagiaire")
                self.remove_from_parent()
                
# Any code you write here will run before the form opens.

    def button_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        alert(self.item['type_stage_txt'])  # est le code du stgae concerné par ce PR

        # Recherche d'un diplome éventuel
        try:
            row = app_tables.stagiaires_inscrits.get(stage_txt=self.item['type_stage_txt'],
                                                     user_email=self.item['stagiaire_email'])
            alert(row['numero'])
            alert(row['name'])
        
            if row['diplome'] is not None:
                file = row['diplome']  # ACQUUISITION DU LAZY MEDIA
            else:
                alert("Pas de document trouvé")
                return
        except Exception as e:
            alert(f"Erreur en recherche de diplôme: {e}")
        # envoi en traitement PDF
        self.traitement_pdf(file)

            
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
            self.item['stage_row'] ,        # stage row
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

        # =========================================================================================================================================
        
        # ENVOI EN UPLINK sur Pi5                          pdf file,  dico
        nb_pages = anvil.server.call("pre_requis_from_pdf", new_file, result)
        print(f"{nb_pages} document sauvé !")

        # on affiche le doc:
        try:
            row_pr = app_tables.pre_requis_stagiaire.get(
                stage_num=self.item['stage_row'],
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
        