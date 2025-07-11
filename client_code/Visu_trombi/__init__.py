from ._anvil_designer import Visu_trombiTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#from .. import anvil_extras
global cpt   # Compte le nb d'images visualisées pour le page Break
cpt = 0


# Visualisation du TROMBI sur un XY panel
class Visu_trombi(Visu_trombiTemplate):
    def __init__(self, num_stage, intitule, pdf_mode=False, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()
        #import anvil.js    # pour screen size
        from anvil.js import window # to gain access to the window object
        global screen_size
        screen_size = window.innerWidth
        
        global cpt
        cpt = 0
        
        self.num_stage = num_stage
        self.intitule = intitule
        self.pdf_mode = pdf_mode
        larg = 175 # largeur image en pixel
        inter = 4  # Interval entre image
       
        if self.pdf_mode is True:
            self.button_annuler.visible = False
            self.button_annuler2.visible = False
            self.button_trombi.visible = False
            self.button_trombi_pdf.visible = False
        else:
            self.button_annuler.visible = True
            self.button_annuler2.visible = True
            self.button_trombi.visible = True
            self.button_trombi_pdf.visible = True
            
        #lecture du fichier père stages
        stage_row = app_tables.stages.get(numero=int(num_stage))    
        cod = stage_row["code"]['code']
        date = str(stage_row["date_debut"].strftime("%d/%m/%Y"))
        self.label_titre.text = "Trombi stagiaires, " + cod + " du " + date + ".   (Stage num " + str(num_stage)+ ")"
        
        # extraction de la liste (fonction list())
        rows = list(app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True),
            stage=stage_row
        ))      
        nb_stagiaires = len(rows)                      # nb de stagiaires
        print("nb-stagiaires", nb_stagiaires)

        """ ***************** BOUCLE sur nb stgiaires ds liste *************"""
        xx = 1   # position (x=1, y=1)
        yy = 1
        cpt_stagiaire = 0
        cpt_ligne = 1
        for row in rows :
    
            cpt_stagiaire += 1  # incrément compteur nb stagiaires
       
            #lecture fichier users à partir du mail
            mel=row["user_email"]['email']
            stagiaire = app_tables.users.get(email=mel)    
            if stagiaire :
                
                #Photo
                table_pic = stagiaire['photo']
                
                self.im = Image(background="white", 
                                    display_mode="shrink_to_fit",
                                    height = larg,
                                    source = table_pic,
                                    spacing_below = None,
                                    horizontal_align = "center",
                                    border = "1px solid black",
                                    visible = True,
                                    tag = mel
                                    )
                #self.im.set_event_handler('mouse_down',self.im_mouse_down)            #POUR RENDRE L'IMAGE CLICKABLE, REVALIDER CETTE LIGNE
                self.im.set_event_handler('show',self.im_show)
                
                # Nom prénom
                try:  #au cas où prenom vide 
                    txt = stagiaire['nom'] + " " + stagiaire['prenom']
                except:
                    txt = stagiaire['nom']
                self.bt = Button(text=txt, tag = mel, spacing_above = None, background="", foreground="blue", bold=True, font_size = 14, enabled = True)
                self.bt.set_event_handler('click',self.bt_click)

                # Tel
                tel=row["user_email"]['tel']
                try:
                    a = tel[0:2]   # mise en forme du tel
                    b = tel[2:4]
                    c = tel[4:6]
                    d = tel[6:8]
                    e = tel[8:10]
                    tel = a+"-"+b+"-"+c+"-"+d+"-"+e    
                except:
                    tel="Tel ?"
                self.bt2 = Button(text=tel, tag = mel, spacing_above = None, background="", foreground="blue", bold=True, font_size = 14, enabled = True)
                self.bt2.set_event_handler('click',self.bt_click)

                # mail
                self.bt3 = Button(text=mel, tag = mel, spacing_above = None, background="", foreground="blue", bold=True, font_size = 12, enabled = True)
                self.bt3.set_event_handler('click',self.bt_click)
                
                self.xy_panel.add_component(self.im, x=xx, y=yy, width = larg)
                self.xy_panel.add_component(self.bt, x=xx, y=yy+larg, width = larg)  #nom,prénom
                self.xy_panel.add_component(self.bt2, x=xx, y=yy+larg+20, width = larg)  #tel
                self.xy_panel.add_component(self.bt3, x=xx, y=yy+larg+40, width = larg)  #tel
                

                if screen_size < 800:
                    nb_img_par_ligne = 4
                else:
                    nb_img_par_ligne = 5
                
                if cpt_stagiaire % nb_img_par_ligne == 0 : # (modulo 5) si 5eme image de la ligne affichée, j'initialise à 1ere image et saute la ligne
                    if cpt_ligne == 5:      # si 5eme image de la 4eme ligne, page break
                        #self.add_component(PageBreak())      # si en création de pdf, je saute une page après 4 lignes
                        cpt_ligne == 0
                       
                    xx = 1
                    yy += 280   # Je descend de 260 pixels pour afficher la prochaine ligne
                    cpt_ligne += 1
                else :                      # pas 4eme image, je décalle à la prochaine image
                    xx = xx + larg + inter
            else:
                """ si pas de stagiaire """
                print("stagiaire non trouvé par son mail")
        self.column_panel_header.scroll_into_view()
                
    """ *************************************************************************************************************************************"""
    """ ******************************              Gestion des évenements click sur image ou nom, extraction grace au TAG de l'image ou nom """
    def bt_click(self, **event_args):
        """This method is called when the link is clicked"""
        """ contenu du dictionaire event_args 
        {'button': 1, 'keys': {'meta': False, 'shift': False, 'ctrl': False, 'alt': False}, 'sender': <anvil.Image object>, 'event_name': 'mouse_down'}"""
        #print(event_args) # c'est un dictionnaire contenant les infos de lévenement
        mel = event_args["sender"].tag   # j'extrai le tag du sender (l'image)
        from ..Saisie_info_apres_visu import Saisie_info_apres_visu
        open_form('Saisie_info_apres_visu', mel, self.num_stage, self.intitule)
  
    def im_mouse_down(self, x, y, **event_args):
        """This method is called when the mouse cursor enters this component"""
        """ contenu du dictionaire event_args 
        {'button': 1, 'keys': {'meta': False, 'shift': False, 'ctrl': False, 'alt': False}, 'sender': <anvil.Image object>, 'event_name': 'mouse_down'}"""
        #print(event_args) #c'est un dictionnaire contenant les infos de lévenement
        mel = event_args["sender"].tag   # j'extrai le tag du sender (l'image)
        #print("mail",mel)
        from ..Saisie_info_apres_trombi import Saisie_info_apres_trombi
        open_form('Saisie_info_apres_trombi', self.num_stage, self.intitule, mel)
    
    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        """
        from ..Stage_visu_modif import Stage_visu_modif
        open_form('Stage_visu_modif', int(self.num_stage), False)  # False: ne pas effectuer les BG tasks
        """
        open_form(self.f)
        
    def button_retour2_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_retour_click()

    def im_show(self, **event_args):
        """This method is called when the Image is shown on the screen"""
        global cpt  # Cpt le nb d'images imprimées
        cpt += 1
        print(cpt)
        if cpt == 25:   
           print("Page Break", cpt)
           self.add_component(PageBreak())      # si en création de pdf, je saute une page ts les 25 images, NE FONCTIONNE PAS !!!

    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_liste_1_stage import Visu_liste_1_stage
        open_form('Visu_liste_1_stage',self.num_stage, self.intitule)

    def button_trombi_pdf_click(self, **event_args):
        """This method is called when the button is clicked"""
        stage_row = app_tables.stages.get(numero=int(self.num_stage))
        pdf = stage_row["trombi_media"]
        if pdf:
            anvil.media.download(pdf)
            alert("Trombinoscope téléchargé")
        else:
            alert("Pdf du trombi non trouvé")

    def button_screenshot_click(self, **event_args):
        """This method is called when the button is clicked"""
        from anvil.js.window import html2canvas
        import anvil.js
        # on inclu pas les boutons dans le pdf
        self.column_panel_boutons.visible = False
        dom_node = anvil.js.get_dom_node(self.column_panel_all)
        canvas = html2canvas(dom_node)
        data_url = canvas.toDataURL("image/jpeg")
        # Ici, tu envoies ton image au serveur...
        pdf = anvil.server.call('pdf_generation', data_url, self.num_stage, "jmmourlhou@gmail.com")
        if pdf:
            anvil.media.download(pdf)
            alert("Trombinoscope téléchargé")
        else:
            alert("Pdf du trombi non trouvé")
         
        
                
     
