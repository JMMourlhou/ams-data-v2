from ._anvil_designer import Visu_trombi_2Template
from anvil import *
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
from ..PageBreak import PageBreak

class Visu_trombi_2(Visu_trombi_2Template):
    def __init__(self, num_stage, intitule, pdf_mode=False, **properties):
        self.init_components(**properties)
        self.f = get_open_form() # form appelante
        
        self.num_stage = num_stage
        self.intitule = intitule
        self.pdf_mode = pdf_mode

        # Boutons visibles seulement hors PDF
        for b in (self.button_annuler, self.button_annuler2, self.button_trombi, self.button_trombi_pdf):
            b.visible = not self.pdf_mode

        # ---- Paramètres d'affichage
        nb_lignes = 2              # nb de lignes par page: 2 pour test puis changer (puis ajouter ds table Global_variables)
        larg = 160                 # largeur image px
        height = larg * 4/3        # ratio 4/3
        inter = 10                 # intervalle horizontal
        pas_ligne = 290            # hauteur d'une "ligne" (image + textes)

        # Nombre d'images par ligne:
        # en mode PDF => fixe (évite toute dépendance à window.innerWidth durant le rendu)
        if self.pdf_mode:
            nb_img_par_ligne = 5
        else:
            # En interactif, tu peux garder ton comportement responsive
            try:
                from anvil.js import window
                nb_img_par_ligne = 4 if window.innerWidth < 800 else 5
            except Exception:
                nb_img_par_ligne = 5

        # ---- Titre
        self.stage_row = app_tables.stages.get(numero=int(num_stage))
        cod = self.stage_row["code"]['code']
        date = str(self.stage_row["date_debut"].strftime("%d/%m/%Y"))
        self.label_titre.text = f"Trombi stagiaires, {cod} du {date}.   (Stage num {num_stage})"

        # ---- Données
        # extraction de la liste (fonction list())
        self.rows = list(app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True),
            stage=self.stage_row
        ))     
        nb_stagiaires = len(self.rows)
        print("nb-stagiaires", nb_stagiaires)

        # ---- Placement absolu dans le XYPanel
        xx = 1
        yy = 1
        cpt_stagiaire = 0
        cpt_ligne = 1  # commence à 1, on veut couper toutes les 2 lignes

        for row in self.rows:
            cpt_stagiaire += 1

            mel = row["user_email"]['email']
            stagiaire = app_tables.users.get(email=mel)
            if not stagiaire:
                print("stagiaire non trouvé par son mail:", mel)
                continue

            table_pic = stagiaire['photo']

            # --- Image
            im = Image(
                background="white",
                display_mode="shrink_to_fit",
                height=height,
                source=table_pic,
                spacing_below=None,
                horizontal_align="center",
                border="1px solid black",
                visible=True,
                tag=mel
            )

            # --- Nom / Tel / Mail
            try:
                nomprenom = f"{stagiaire['nom']} {stagiaire['prenom']}"
            except Exception:
                nomprenom = stagiaire.get('nom') or ''

            tel = row["user_email"].get('tel') or "Tel ?"
            try:
                if len(tel) == 10 and tel.isdigit():
                    tel = f"{tel[0:2]}-{tel[2:4]}-{tel[4:6]}-{tel[6:8]}-{tel[8:10]}"
            except Exception:
                pass

            nom_p = TextArea(text=nomprenom, tag=mel, background="white", foreground="blue",
                             font_size=13, align="center", auto_expand=False)
            tel_t = TextArea(text=tel, tag=mel, background="white", foreground="blue",
                             font_size=13, align="center", auto_expand=False)
            mail_t = TextArea(text=mel, tag=mel, background="white", foreground="blue",
                              font_size=10, align="center", auto_expand=False)

            # --- Ajout dans le XYPanel aux coordonnées calculées
            self.xy_panel.add_component(im,     x=xx, y=yy,                width=larg)
            self.xy_panel.add_component(nom_p,  x=xx, y=yy + height - 45,  width=larg)
            self.xy_panel.add_component(tel_t,  x=xx, y=yy + height - 20,  width=larg)
            self.xy_panel.add_component(mail_t, x=xx, y=yy + height + 5,   width=larg)

            # --- Passage à l'image suivante / gestion de fin de ligne
            if (cpt_stagiaire % nb_img_par_ligne) == 0:
                # fin de ligne
                xx = 1
                yy += pas_ligne
                cpt_ligne += 1

                # ⬇️ saut de page toutes les  'nb_lignes' lignes (et pas après la dernière)
                if (cpt_ligne %  nb_lignes == 1) and (cpt_stagiaire != nb_stagiaires):
                    # IMPORTANT : insérer le PageBreak dans le CONTENEUR parent linéaire qui englobe le xy_panel.
                    #  Ici j'utilise column_panel_all.
                    self.column_panel_all.add_component(PageBreak(margin_top=24))
                    print("saut de page")
            else:
                # même ligne, on avance en X
                xx += larg + inter

        # Petit confort
        self.column_panel_header.scroll_into_view()

    # (supprime im_show si tu l'utilisais pour forcer les coupures)
    def im_show(self, **event_args):
        pass

    """ *************************************************************************************************************************************"""
    """ ******************************              Gestion des évenements click sur image ou nom, extraction grace au TAG de l'image ou nom """

    def bt_click(self, **event_args):
        """This method is called when the link is clicked"""
        """ contenu du dictionaire event_args 
        {'button': 1, 'keys': {'meta': False, 'shift': False, 'ctrl': False, 'alt': False}, 'sender': <anvil.Image object>, 'event_name': 'mouse_down'}"""
        # print(event_args) # c'est un dictionnaire contenant les infos de lévenement
        mel = event_args["sender"].tag  # j'extrai le tag du sender (l'image)
        from ..Saisie_info_apres_visu import Saisie_info_apres_visu

        open_form("Saisie_info_apres_visu", mel, self.num_stage, self.intitule)

    def im_mouse_down(self, x, y, **event_args):
        """This method is called when the mouse cursor enters this component"""
        """ contenu du dictionaire event_args 
        {'button': 1, 'keys': {'meta': False, 'shift': False, 'ctrl': False, 'alt': False}, 'sender': <anvil.Image object>, 'event_name': 'mouse_down'}"""
        # print(event_args) #c'est un dictionnaire contenant les infos de lévenement
        mel = event_args["sender"].tag  # j'extrai le tag du sender (l'image)
        # print("mail",mel)
        from ..Saisie_info_apres_trombi import Saisie_info_apres_trombi

        open_form("Saisie_info_apres_trombi", self.num_stage, self.intitule, mel)

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

    """
    def im_show(self, **event_args):
        # This method is called when the Image is shown on the screen
        global cpt  # Cpt le nb d'images imprimées
        cpt += 1
        print(cpt)
        if cpt == 25:
            print("Page Break", cpt)
            self.add_component(
                PageBreak()
            )  # si en création de pdf, je saute une page ts les 25 images, NE FONCTIONNE PAS !!!
    """
    
    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_liste_1_stage import Visu_liste_1_stage

        open_form("Visu_liste_1_stage", self.num_stage, self.intitule)

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

        # 1. on inclu pas les boutons dans le pdf
        self.column_panel_boutons.visible = False

        # 2. Force un ratio précis sur le xy_panel avant la capture
        # self.xy_panel.width = 900
        # self.xy_panel.height = 1200   # ratio 4/3

        # 3.copie du composant et transformation en jpg
        dom_node = anvil.js.get_dom_node(self.column_panel_all)
        canvas = html2canvas(dom_node)
        data_url = canvas.toDataURL("image/jpeg")

        # Envoie de l'image au serveur...
        pdf = anvil.server.call(
            "pdf_generation", data_url, self.num_stage
        )  # fonctionne qd l'app est lancée du Pi5, docker ct
        # récupération du pdf
        if pdf:
            anvil.media.download(pdf)
            alert("Trombinoscope téléchargé")
        else:
            alert("Pdf du trombi non trouvé")

    def button_visu_html_click(self, **event_args):
        """This method is called when the button is clicked"""
        pdf = anvil.server.call(
            "make_trombi_pdf_via_uplink",
            self.stage,
            self.rows,
            self.num_stage,
            self.intitule,
            cols=5,            # 4 ou 5 colonnes
            lines_per_page=2,  # saut de page toutes les 2 lignes
            title_enabled=True
        )
        if pdf:
            anvil.media.download(pdf)
            alert("Trombinoscope html téléchargé")
        else:
            alert("Pdf du trombi html non trouvé")
