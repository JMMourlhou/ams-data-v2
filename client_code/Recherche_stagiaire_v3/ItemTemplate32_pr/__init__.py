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
from ...Pre_Visu_img_Pdf import Pre_Visu_img_Pdf   #pour afficher un document avant de le télécharger
from datetime import datetime
from anvil.js import window # pour screen size

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
                "date_expiration":   date_expiration
        """
        self.screen_size = window.innerWidth
        if self.screen_size < 800:    
            self.button_visu.visible = False
        else:
            self.button_visu.visible = True
            
        # Any code you write here will run before the form opens.
        self.date_du_jour = datetime.now(anvil.tz.tzlocal()).date()  # pour comparer avec date d'expiration
        self.test_img_just_loaded = False

        #self.email = self.item['stagiaire_email']
        self.stagiaire_row = self.item['stagiaire_email']
        self.stage_num = self.item['stage_row']                # =================================

        txt0 = self.item['stage_row']['code_txt']+" / "  # le stage
        txt1 = self.item['stagiaire_email']['nom']+"."+self.item['stagiaire_email']['prenom'][0]+"   /   "
        txt2 = self.item['requis_txt']  # l'intitulé
        self.label_en_tete_pr.text = txt0 +txt1 + txt2

        # Affichage et couleurs de la date d'expiration et bt efface
        self.date_picker_1.date = self.item['date_expiration']
        
        # -------------------------------------------------
        # lecture de la table Mère Pre_Requis pour afficher ou non la date d'expiration et déterminer les couleurs
        if self.item['item_requis']['Expiration'] is True:
            # on affiche l'élément date_picker_1 et son contenu
            self.date_picker_1.visible = True 
            self.date_picker_1.date = self.item['date_expiration']  
            if self.date_picker_1.date is not None:
                self.button_efface_date_expiration.visible = True

            if self.item['doc1'] is None:  # le pré-requis absent: erreur
                self.date_picker_1.background = "theme:Error"
                self.date_picker_1.foreground = "white"
            else:  # pré-Requis affiché, test sur la date d'expiration
                if self.item['date_expiration']is not None and self.item['date_expiration'] < self.date_du_jour: 
                    self.date_picker_1.background = "theme:Error"
                    self.date_picker_1.foreground = "white"
                else:
                    self.date_picker_1.background = "theme:Vert Clair"
                    self.date_picker_1.foreground = "white"   

            # Si le pré requis est affiché, mais pas la date d'expiration : Erreur
            if self.item['doc1'] is not None and self.date_picker_1.date is None: 

                self.date_picker_1.background = "theme:Jaune Vert"
                self.date_picker_1.foreground = "dark"
        else:
            self.date_picker_1.visible = False
            self.button_efface_date_expiration.visible = False
        # -------------------------------------------------
        if self.item['doc1'] is not None:
            self.image_1.source = self.item['doc1']        
            
            self.button_del.visible = True
            self.button_visu.visible = True
            self.file_loader_1.visible = False
            self.button_del_pour_ce_stagiaire.visible = False
            self.button_rotation.visible = True
            self.button_download.visible = True
        else:
            self.image_1.source = None       # permet de tester le click sur l'image
            self.button_del.visible = False
            self.button_visu.visible = False
            self.file_loader_1.visible = True
            self.button_del_pour_ce_stagiaire.visible = True
            self.button_rotation.visible = False
            self.button_download.visible = False
            
        #print(f"<{self.item['item_requis']['code_pre_requis'][0:6].strip()}>")
        #print(f"<{self.item['item_requis']['code_pre_requis'].strip()}>")
        # si on recherche un diplome ou une attestation
        if (self.item['item_requis']['code_pre_requis'].strip() in ("DIP-BNSSA", "DIP-PSE1", "DIP-PSE2", "DIP-PSC") or self.item['item_requis']['code_pre_requis'].strip().startswith("ATT-FC")) and self.image_1.source is None: 
            self.button_search.visible = True
        else:
            self.button_search.visible = False

        if self.image_1.source is not None and  self.screen_size > 800 and not self.column_panel_content.get_components():       
            self.button_visu.visible = True

            
    def button_visu_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Relecture du row de la table pre_requis_stagiaire: (self.item nest pas le row du pre requis)
        if self.image_1.source is not None and  self.screen_size > 800 and not self.column_panel_content.get_components():
            try:
                row = app_tables.pre_requis_stagiaire.get(
                    stage_num=self.item['stage_row'],
                    stagiaire_email=self.item['stagiaire_email'],
                    item_requis=self.item['item_requis']
                )
            except Exception as e:
                alert(f"Erreur de relecture du row pre_requis_stagiaire: {e}")
                return
            # nouveau nom doc
            self.label_en_tete_pr.scroll_into_view(align="start")
            new_file_name = Pre_R_doc_name.doc_name_creation(row['stage_num'], row['requis_txt'], row['stagiaire_email'])   # extension non incluse
            self.column_panel_content.add_component(Pre_Visu_img_Pdf(row['doc1'], new_file_name, self.stage_num, row['stagiaire_email'], row['item_requis'], origine="pre-requis-admin"))
            self.label_en_tete_pr.scroll_into_view(align="start")

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
                self.button_download.visible = True
                self.button_visu.visible = True  
                self.button_del.visible = True 
            elif file_extension == ".pdf":      
                self.traitement_pdf(file)
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
            self.button_download.visible = False

            self.file_loader_1.text = ""
            self.file_loader_1.font_size = 18
            self.file_loader_1.visible = True
            self.button_del_pour_ce_stagiaire.visible = True
        else:
            alert("Pré Requis non enlevé")


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
        screen_size = window.innerWidth
        # non Vide et pas tel, et l'image non déjà affichée ds column_panel_content je peux cliquer sur l'image
        if self.image_1.source is not None and  screen_size > 800 and not self.column_panel_content.get_components():       
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
        #alert(self.item['item_requis']['code_pre_requis'])  # est le code du PR recherché ds le stage qui lui coorespond
        if self.item['item_requis']['code_pre_requis'].strip() in ("DIP-BNSSA", "DIP-PSE1", "DIP-PSE2", "DIP-PSC"):
            # j'extrais le type de stage après 'DIP-' (après le 4eme caract, jusquà la fin)
            stage = self.item['item_requis']['code_pre_requis'].strip()[4:]
            
        if self.item['item_requis']['code_pre_requis'].strip().startswith("ATT-"):
            # j'extrais le type de stage après 'ATT-'
            stage = self.item['item_requis']['code_pre_requis'].strip()[4:]
            
        #alert(f"stage recherché: {stage}")  
        # Recherche d'un diplome éventuel dans table stagiaires_inscrits
        rows = app_tables.stagiaires_inscrits.search(tables.order_by("numero", ascending=False),    # le plus récent d'abord
                                                    stage_txt=stage,
                                                    user_email=self.item['stagiaire_email'])
        #alert(f"nb de rows: {len(rows)}")
        if len(rows)>=1:  # il peut y avoir plusieurs stages ex: plusieurs inscriptions au BNSSA avec le rattrapage, plusieurs FC PSE ...
            for row in rows:
                if row['diplome'] is not None:
                    file = row['diplome']  # ACQUISITION DU LAZY MEDIA
                    # envoi en traitement PDF
                    self.traitement_pdf(file)
                    continue
        else:
            alert(f"Pas de doc '{self.item['item_requis']['code_pre_requis'].strip()}' trouvé dans les stages AMS précédents")
        
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
        #                                                                          Fin de Création du dico
        # =========================================================================================================================================
        
        # ENVOI EN UPLINK sur Pi5                          pdf file,  dico
        nb_pages = anvil.server.call("pre_requis_from_pdf", new_file, result, 'unik')  # unik indique qu'il n'y aura que la 1er page à prendre même s'ily a plusieurs pages
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
        self.button_search.visible = False
        # gestion des boutons        
        self.file_loader_1.visible = False
        self.button_rotation.visible = True
        self.button_visu.visible = True  
        self.button_del.visible = True 

        end = French_zone.french_zone_time()
        temps = f"Temps de traitement image: {end-start}"
        print(temps)


    def button_efface_date_expiration_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.date_picker_1.date = None
    
        # Sauvegarde la date_d'exp vide, effacement à True 
        result = anvil.server.call('pr_expiration_date_writting', self.item, None, True) 
        if result != "Ok":
            alert(result)

    def date_picker_1_change(self, **event_args):
        """This method is called when the selected date changes"""
        date_selectionnee = self.date_picker_1.date
        if date_selectionnee is None :
            alert("Aucune date sélectionnée")
            return
        if date_selectionnee is not None and date_selectionnee < self.date_du_jour: 
            self.date_picker_1.background = "theme:Error"
            self.date_picker_1.foreground = "white"
        else:
            self.date_picker_1.background = "theme:Vert Clair"
            self.date_picker_1.foreground = "white" 

        # Sauvegarde
        result = anvil.server.call('pr_expiration_date_writting', self.item, date_selectionnee)
        if result != "Ok":
            alert(result)

    def button_download_click(self, **event_args):
        """This method is called when the button is clicked"""
        new_file_name = Pre_R_doc_name.doc_name_creation(self.item['stage_row'], self.item['requis_txt'], self.item['stagiaire_email'])   # extension non incluse
        new_file_named = anvil.BlobMedia("image/jpg", self.image_1.source.get_bytes(), name=new_file_name+".jpg")
        anvil.media.download(new_file_named)
        n = Notification("Téléchargement effectué !",
                         timeout=1)   # par défaut 2 secondes
        n.show()
            