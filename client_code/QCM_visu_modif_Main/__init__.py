from ._anvil_designer import QCM_visu_modif_MainTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Main import Main
from ..QCM_visu_modif import QCM_visu_modif
global liste
liste = []
# ==========================================================================   Ellaboration d'un QCM par un formateur ou admin
class QCM_visu_modif_Main(QCM_visu_modif_MainTemplate):
    def __init__(self, qcm_descro_nb=None, **properties):      #qcm_descro_nb n'est pas None si je suis en réaffichage après création ou maj d'1 question du qcm 
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        #self.word_editor_1.visible = False   # Pour ne pas afficher tout de suite le Word processor
        # ----------------------------------------------------A mettre en BG task: Vérif des qcm_sources en table Qcm desco
        liste_sources = app_tables.qcm_description.search()
        for qcm in liste_sources:
            tag_sov = False
            if qcm['exam'] is False:
                # valeur est le nb de questions
                cle = str(qcm['qcm_nb'])
                nb_questions_real = str(len(app_tables.qcm.search(qcm_nb=qcm)))
                if qcm['qcm_source'] is None:
                    print(f"création, cle; {cle} valeur: {nb_questions_real}")       
                    tag_sov = True
                else:
                    # Il y a déjà une colonne source pour ce qcm: Vérif si nb de questions à jour 
                    dico = qcm['qcm_source']
                    nb_questions_dico = dico[cle]
                    if nb_questions_dico != nb_questions_real:
                        tag_sov = True
                        print(f"modif , cle; {cle} nb questions réelles: {nb_questions_real}, anciennement: {nb_questions_dico} ")      
                if tag_sov is True:
                    # envoi en écriture
                    r = anvil.server.call("change_source_qcm", qcm, nb_questions_real)
                    if not r:
                        alert(f"Erreur en MAJ du source du Qcm {cle}")
                        return
        # initialisations
        #self.column_panel_question.visible = False
        # initilisation du drop down menu (voir lignes 500)
        self.drop_down_menu.items=([("Créer un nouveau QCM 'standard'", 0),
                                    ("Créer un nouveau QCM 'examen'", 1),
                                    ("Modifier un QCM", 2),
                                    ("Effacer un QCM", 3),
                                    ("Affecter un QCM à un stage", 4),
                                   ])
    
        #initialisation des drop down des qcm créés et barêmes
        #self.image_1.source = None
        self.drop_down_qcm_row.items = [(r['destination'], r) for r in app_tables.qcm_description.search(tables.order_by("destination", ascending=True))]
        #self.drop_down_bareme.items=["1","2","3","4","5","10"]
        #self.drop_down_bareme.selected_value = "1"
        #self.drop_down_nb_options.items=([("Vrai/Faux", 1), ("2 options", 2), ("3 options", 3), ("4 options", 4), ("5 options", 5)])
        # ______________________________________________________________________________________________________________
        #initialisation drop down owner,  propriétaires potentiels, tous sauf "S",
        liste = app_tables.users.search(
                                            q.fetch_only("nom","prenom","email","role"),
                                            tables.order_by("prenom", ascending=True),
                                            q.not_ (role = "S")
                                        )
        liste2 = []
        for qcm_owner in liste:
            liste2.append((qcm_owner["prenom"]+" "+qcm_owner["nom"],qcm_owner))    # doit renvoyer user row pour la création du qcm
        self.drop_down_owner.items=liste2
        try:
            user=anvil.users.get_user()
            self.drop_down_owner.selected_value = user    # essai d'initialiser la drop down sur le user 
        except:
            pass
        self.text_box_destination.focus()
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  Ré-affichage ?   +++++++++++++++++++++++++++++
        if qcm_descro_nb is not None:      #réinitialisation de la forme après une création ou modif
            self.qcm_nb = qcm_descro_nb # je sauve le row du qcm sur lesquel je suis en train de travailler
            # j'affiche le drop down du qcm
            self.drop_down_qcm_row.selected_value = qcm_descro_nb
            # j'initialise le drop_down_menu à 2 (modif d'un QCM)
            self.drop_down_menu.selected_value = 2
            # j'envoie en drop_down_qcm_row_change
            self.drop_down_qcm_row_change()
        

    # L'utilisateur a cliqué sur un QCM à modifier, affichage de ses caractéristiques
    def drop_down_qcm_row_change(self, **event_args):
        """This method is called when an item is selected"""
        self.qcm_row = self.drop_down_qcm_row.selected_value
        self.drop_down_qcm_row.visible = False
        self.user=anvil.users.get_user()

        # test s'il est le propriétaire ou A ou B
        #alert(self.qcm_row["qcm_owner"]["email"])
        if self.qcm_row["qcm_owner"]["email"] != self.user["email"] and self.user["role"] != "B" and self.user["role"] != "A" :
            alert("Vous n'êtes pas le propriétaire de ce QCM, \nVous ne pouvez pas le modifier !")
            # Réinitialisation
            open_form("QCM_visu_modif_Main", None)
            
        # Si je suis l'admin, je peux MAJ le num du qcm, au cas où ...
        if self.user["role"] == "A":
            self.text_box_num_qcm.enabled = True
        # __________________________________________________________ CREATION QCM   /   MODIF INTITULE, owner, visible, examen
        self.text_box_num_qcm.text = self.qcm_row["qcm_nb"]
        self.sov_num_qcm = self.qcm_row["qcm_nb"]
        self.text_box_destination.text = self.qcm_row["destination"]
        self.sov_destination = self.qcm_row["destination"]  # pour test si 2 destinations identiques en modif 
        self.drop_down_owner.selected_value = self.qcm_row["qcm_owner"]
        self.check_box_visible.checked = self.qcm_row["visible"]
        self.check_box_examen.checked = self.qcm_row["exam"]           # EXAM ? si oui ne pas afficher le colomn panel question, afficher col panel des enfants qcm exam
        self.column_panel_creation_qcm.visible = True
        # _______________________________________________________________________________
        # Pour les lignes QCM déjà crées du qcm choisi
        global liste
        liste = list(app_tables.qcm.search(qcm_nb=self.qcm_row))
        nb_questions = len(liste)
        #print("nb questions: ", nb_questions)
        #num_question = str(nb_questions + 1)
        #self.label_2.text = nb_questions + 1  # Num ligne à partir du nb lignes déjà créées

        # modif du user's temp (nb de questions de son qcm)
        
        r = anvil.server.call("temp_user_qcm", self.user, nb_questions, self.qcm_row["qcm_nb"])
        if r is False:
            alert("user non MAJ")
            return
            
        # Affiche button Test si au moins 1 question existe déjà
        if nb_questions > 1:
            self.button_test.visible = True

        # Je ne permets pas de modif du type de qcm: exam ou pas
        self.check_box_examen.enabled = False
        # Si ce qcm est de type examen, je n'affiche pas le colomn panel des questions
        if  self.qcm_row["exam"] is not True:  
            # affiches les lignes du qcm
            self.label_3.text = "Mise à jour du Q.C.M " + self.qcm_row["destination"]
            #self.column_panel_question.visible = True
            self.affiche_lignes_qcm(liste)
        else: # QCM exam: je n'affiche pas de lignes questions qcm mais les qcm enfants potentiels
            self.column_panel_question.visible = False
            self.dict = self.qcm_row["qcm_source"]
            
            # Tous les qcm qui ne sont pas exam
            self.liste_qcm_descro = app_tables.qcm_description.search(tables.order_by("destination", ascending=True),
                                                                     exam=False)  
            
            # panel des qcms disponibles (MOINS LES QCM enfants DEJA SELECTIONNES POUR CE STAGE)
            liste_qcm_dispos = []
            liste_qcm_selectionnes = []
            if self.dict is not None and self.dict != {}:     # ni None, ni {}
                # Enlever les qcm déjà sélectionnés
                for qcm in self.liste_qcm_descro:
                    valeur = self.dict.get(str(qcm['qcm_nb']))   # recherche sur le num du qcm (doit être str)
                    if valeur is None:  
                        # ce qcm n'est pas ds le dict du stage, je l'affiche ds panel 1, qcm dispos
                        print(qcm['destination'])
                        #                        0             1              2                   
                        #                        qcm_exam    , qcm enfant nb, qcm_destination,   
                        liste_qcm_dispos.append((self.qcm_row, qcm['qcm_nb'], qcm['destination']))
                    else: # ce qcm est ds le dict du stage, je l'affiche ds panel 2, qcm selectionnés
                        #                              0             1              2                 3
                        #                              qcm_exam_row    , qcm enfant nb, qcm_destination,  nb de questions
                        liste_qcm_selectionnes.append((self.qcm_row, qcm['qcm_nb'], qcm['destination'], valeur)) 
            else: # si pas de dict, j'affiche ts les qcm
                for qcm in self.liste_qcm_descro:
                    liste_qcm_dispos.append((self.qcm_row, qcm['qcm_nb'], qcm['destination'], qcm['visu_qcm_par_stage']))
                    liste_qcm_selectionnes = []
                    
            self.column_panel_exam.visible = True
            print(f"Nb de qcm dipos: {len(liste_qcm_dispos)}")
            #self.repeating_panel_1.visible = True
            self.repeating_panel_1.items = liste_qcm_dispos
    
            print(f"Nb de qcm sélectionnés: {len(liste_qcm_selectionnes)}") 
            #self.repeating_panel_2.visible = True
            self.repeating_panel_2.items = liste_qcm_selectionnes
                        

    def affiche_lignes_qcm(self, l=[]):
        global liste
        self.column_panel_content.clear()
        self.column_panel_content.add_component(QCM_visu_modif(liste), full_width_row=True)

    def file_loader_photo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        thumb_pic = anvil.image.generate_thumbnail(file, 640)
        self.image_1.source = thumb_pic
        self.column_panel_img.visible = True
        self.button_creer.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def drop_down_nb_options_change(self, **event_args):
        """This method is called when an item is selected"""
        self.drop_down_menu.visible = False  # effacer le menu si pas fait
        self.rep1.checked = False
        self.rep2.checked = False
        self.rep3.checked = False
        self.rep4.checked = False
        self.rep5.checked = False
        choix = self.drop_down_nb_options.selected_value
        #print(choix, type(choix))
        question_part1 = """<!-- Question -->
                            <p
                            style="
                                margin-bottom: 10px;
                                text-align: left;
                                font-weight: bold;
                                color: rgb(0, 192, 250);
                            "
                            >
                            <span
                                style="
                                background-color: var(--anvil-color-On-Secondary-Container-94f5);
                                padding: 2px 6px;
                                border-radius: 4px;
                                margin-right: 6px;
                                "
                            >
                                Question :
                            </span>
                            Texte de la question ici
                            </p>
                        """
        
        if choix == 1:   # Vrai/ Faux    l'1 ou l'autre, rep1 et rep2 ne peuvent pas  être identiques
            self.rep3.visible = False
            self.rep4.visible = False
            self.rep5.visible = False
            self.rep1.text = "Vrai"
            self.rep2.text = "Faux"
            self.word_editor_1.text = question_part1
            
        if choix > 1:     # 2 options possibles, rep1 et rep2 peuvent être identiques  ex 11 
            self.rep1.text = "A"
            self.rep2.text = "B"
            self.rep3.visible = False
            self.rep4.visible = False
            self.rep5.visible = False
            self.text_box_question.text = "titre\n\nA  .\n\nB  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        </ul>
                                    """
            
        if choix > 2:     # au moins 3 options possibles, rep1 à rep3 peuvent être identiques  ex 111
            self.rep3.visible = True
            self.rep4.visible = False
            self.rep5.visible = False
            self.text_box_question.text = "titre\n\nA  .\nB  .\nC  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        <li>C</li>
                                        </ul>
                                    """
        if choix > 3:     # au moins 4 options possibles, rep1 et rep4 peuvent être identiques  ex  1111
            self.rep4.visible = True
            self.rep5.visible = False
            self.text_box_question.text = "titre\n\nA  .\nB  .\nC  .\nD  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        <li>C</li>
                                        <li>D</li>
                                        </ul>
                                    """
        if choix > 4:     # 5 options possibles, rep1 à rep2 peuvent être identiques
            self.rep5.visible = True
            self.text_box_question.text = "titre\n\nA  .\nB  .\nC  .\nD  .\nE  ."
            self.word_editor_1.text = question_part1 + """
                                        <ul>
                                        <li>A</li>
                                        <li>B</li>
                                        <li>C</li>
                                        <li>D</li>
                                        <li>E</li>
                                        </ul>
                                    """
        
        self.column_panel_img.visible = True
        self.text_box_correction.visible = True
        self.text_box_question.visible = False 
        # -----------------------------------------------------------------------
        self.word_editor_1.visible = True  # Affiche le component 'Word_Editor'
        self.word_editor_1.param1 = "creation"
        self.word_editor_1.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie_modif)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        
        # -----------------------------------------------------------------------
        self.column_panel_options.visible = True
        self.button_creer_couleurs()

    """
    #===================================================================================================================================================
    RETOUR DU WORD EDITOR  
    # ==================================================================================================================================================
    """
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form (modif du text de base de l'évènement)
    def handle_click_fin_saisie_modif(self, sender, **event_args):
        # sender.text contains the 'Word_editor'form's HTML text
        mode = sender.param1       # mode 'modif' /  'creation' 
        self.text = sender.text    # texte html de la question
        #self.content_panel.clear()  #effacement du content_panel
        if mode == "modif":
            self.button_modif_click(self.text)
        if mode == "creation":
            self.button_creer_click(self.text)
        if mode == "exit":
            self.button_annuler_click()
    """
    Fin RETOUR DU WORD EDITOR  
    """  
        

    def text_box_question_change(self, **event_args):   # Question a changé
        """This method is called when the text in this text box is edited"""
        self.button_creer_couleurs()

    def text_box_correction_change(self, **event_args):
        """This method is called when the text in this text area is edited"""
        self.button_creer_couleurs()

    def drop_down_bareme_change(self, **event_args):     # Bareme a changé
        """This method is called when this checkbox is checked or unchecked"""
        self.button_creer_couleurs()

    def check_box_reponse_change(self, **event_args):   # Reponse a changé:
        """This method is called when this checkbox is checked or unchecked"""
        self.button_creer_couleurs()

    def button_creer_couleurs(self): # qd changement
        self.button_creer.enabled = True
        self.button_creer.background = "red"
        self.button_creer.foregroundground = "yellow"

    def button_creer_click(self, text, **event_args):   #ce n'est que l'orsque le user a clicker sur modif que je prend le contenu
        """This method is called when the button is clicked"""
        if text == "":
            alert("La question est vide !")
            return
        if self.drop_down_bareme.selected_value is None:
            alert("Choisissez un barême !")
            return
        #qst = text
        #qst = qst.strip()
        question = text

        cor = self.text_box_correction.text
        cor = cor.strip()
        correction = cor
        bareme = int(self.drop_down_bareme.selected_value)
        qcm_nb = self.drop_down_qcm_row.selected_value

        if self.image_1.source != "":
            image = self.image_1.source
        else:
            image = None
        # creation de la réponse multi en fonction du nb d'options choisies +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        reponse = ""
        if self.rep1.checked is True:
            r1 = "1"
        else: 
            r1 = "0"
        if self.rep2.checked is True:
            r2 = "1"
        else: 
            r2 = "0"
        if self.rep3.checked is True:
            r3 = "1"
        else: 
            r3 = "0"
        if self.rep4.checked is True:
            r4 = "1"
        else: 
            r4 = "0"
        if self.rep5.checked is True:
            r5 = "1"
        else: 
            r5 = "0"
        if self.drop_down_nb_options.selected_value == 1 or self.drop_down_nb_options.selected_value == 2:    
            reponse = r1 + r2
        if self.drop_down_nb_options.selected_value == 3:
            reponse = r1 + r2 + r3
        if self.drop_down_nb_options.selected_value == 4:
            reponse = r1 + r2 + r3 + r4
        if self.drop_down_nb_options.selected_value == 5:
            reponse = r1 + r2 + r3 + r4 + r5
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  NUM question   +++++++++++++++++++++++++++++
        num = int(self.label_2.text) #je connais le num de question à changer
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  type de question   +++++++++++++++++++++++++++++
        if self.drop_down_nb_options.selected_value == 1:    # type V/F
            type = "V/F"       # rep1 ou rep2 peuvent être vrai
        else:
            type = "Multi"     # rep1 et rep2 peuvent être vrai 
            
        # param (descro du QCM)
        param = self.drop_down_qcm_row.selected_value["destination"]
                    
        # je récupère mes variables globales  question, reponse, bareme
        result = anvil.server.call("add_ligne_qcm", num, question, correction, reponse, bareme, image, qcm_nb, type, param)         #num du stage  de la ligne
        if result:
            n = Notification("Création de la question !",
                 timeout=1)   # par défaut 2 secondes
            n.show()
            # raffraichit les lignes qcm en récupérant le choix du qcm ds la dropdown
            from anvil import open_form       # j'initialise la forme principale avec le choix du qcm ds la dropdown
            open_form("QCM_visu_modif_Main", qcm_nb)
        else:
            alert("erreur de création d'une question QCM")

    def rep1_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.drop_down_nb_options.selected_value == 1:    # option vrai/faux
            if self.rep1.checked is True:   
                self.rep2.checked = False
            else:
                self.rep2.checked = True

    def rep2_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.drop_down_nb_options.selected_value == 1:    # option vrai/faux
            if self.rep2.checked is True:   
                self.rep1.checked = False
            else:
                self.rep1.checked = True

    def rep3_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_creer_couleurs()

    def rep4_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_creer_couleurs()

    def rep5_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_creer_couleurs()

    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    
    #   _________________________________________________________________________________________________________
    #                             Test D'UN QCM
    #   _________________________________________________________________________________________________________    

    def button_test_click(self, **event_args):
        """This method is called when the button is clicked"""

        # Concepteur du qcm demande un test du qcm qu'il met à jour
        # écriture ds table user, colonne 'temp2' : "test" 
        user=anvil.users.get_user()
        if user:
            result = anvil.server.call("modify_users_temp2", user, "test")
            self.affiche_lignes_qcm()
            result = anvil.server.call("modify_users_temp2", user, None)   # je remets temp2 à vide

    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    
    #   _________________________________________________________________________________________________________
    #                             CREATION D'UN QCM
    #   _________________________________________________________________________________________________________
    def creation(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_creation_qcm.visible = True
        self.creation_question.visible = False
        self.column_panel_content.visible = False
        self.button_del.visible = False
        self.drop_down_qcm_row.visible = False
        self.check_box_examen.enabled = False
        self.text_box_destination.focus()
        
        # initialisation du nx num de QCM en lisant le plus grand nb + 1
        plus_grand_row = app_tables.qcm_description.search(tables.order_by("qcm_nb", ascending=False))[0]
        nb_qcm = plus_grand_row['qcm_nb']
        self.text_box_num_qcm.text=nb_qcm+1
    
    def text_box_num_lost_focus(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_del.visible = False
        num = int(self.text_box_num_qcm.text)
        test = app_tables.qcm_description.search(qcm_nb=num)
        if len(test)==1 and self.text_box_num_qcm.text != str(self.sov_num_qcm):
            alert("Ce numéro de Qcm existe déjà, changez le !")
            self.text_box_num_qcm.focus()
            return 
        alert("Ne changer le code du QCM que s'il n'a pas été affecté à un stage !")
        self.button_valid.visible = True

    def text_box_num_qcm_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_del.visible = False
        self.button_valid.visible = True
        
    def text_box_destination_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        # La destination de ce qcm existe-t-elle déjà en dehors d'elle ?
        self.button_del.visible = False
        test = app_tables.qcm_description.search(destination=self.text_box_destination.text)
        if len(test)==1 and self.text_box_destination.text != self.sov_destination:
            alert("La description du QCM existe déjà, changez la !")
            self.text_box_destination.focus()
            return 
        self.button_valid.visible = True
            
    def drop_down_owner_change(self, **event_args):
        """This method is called when an item is selected"""
        # je permet le changement s'il est le propriétaire ou admin ou bureau
        # test s'il est le propriétaire et soit A B 
        if self.qcm_row["qcm_owner"]["email"] != self.user["email"] and self.user["role"] != "B" and self.user["role"] != "A" :
            alert("Vous n'êtes pas le propriétaire de ce QCM, \nVous ne pouvez pas le modifier !")
            # Réinitialisation
            open_form("QCM_visu_modif_Main", None)
        self.button_valid.visible = True

    def check_box_visible_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.button_valid.visible = True
    
    def button_valid_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Description > 5 caractères ?
        if len(self.text_box_destination.text) < 5:
            alert("La description du QCM doit être supérieure à 5 caractères !")
            self.text_box_destination.focus()
            return
            
        # Un propriétaire doit être choisi
        if self.drop_down_owner.selected_value is None:
            alert("Choisissez un propriétaire ! ")
            self.text_box_destination.focus()
            return

        # ECRITURE DANS LA TABLE   _________________________________CREATION
        menu = self.drop_down_menu.selected_value
        #alert(f"menu: {menu}")
        if menu==0 or menu==1:    # créer qcm
            # CREATION:  envoi en écriture si validation
            # La destination de ce nouveau qcm existe-t-elle déjà ?
            test = app_tables.qcm_description.search(destination=self.text_box_destination.text)
            if len(test) == 1:
                alert("La description du QCM existe déjà, changez la !")
                self.text_box_destination.focus()
                return
            
            r=alert("Confirmez la création de ce QCM ?",dismissible=False,buttons=[("oui",True),("non",False)])
            if r :   # oui
                result = anvil.server.call("qcm_création", self.text_box_num_qcm.text,
                                                                    self.text_box_destination.text,
                                                                    self.drop_down_owner.selected_value,   # user row
                                                                    self.check_box_visible.checked,
                                                                    self.check_box_examen.checked
                                                )
                if result is not True:
                    alert("Création du Qcm non effectué !")
                    self.button_valid.visible = False
                    return
                
                # Je sors pour réinitiliser entierrement ce processus
                open_form('Main',99)
                
        
        # ECRITURE DANS LA TABLE   _________________________________ Modification      
        if menu==2:    # modif qcm
            # Modification:  envoi en modif si validation   
            qcm_row = self.drop_down_qcm_row.selected_value
            r=alert("Confirmez la modification de la description de ce QCM ?",dismissible=False,buttons=[("oui",True),("non",False)])
            if r :   # oui
                result = anvil.server.call("qcm_modif", qcm_row,
                                                        self.text_box_num_qcm.text,
                                                        self.text_box_destination.text,
                                                        self.drop_down_owner.selected_value,   # user row
                                                        self.check_box_visible.checked,
                                                        self.check_box_examen.checked
                                                )
                if result is not True:
                    alert("Modification du Qcm non effectuée !")
                    return
                else:
                    alert("Modification du Qcm effectuée !") 
                    self.button_valid.visible = False
                    
    # Effacement d'un qcm
    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        qcm_row = self.drop_down_qcm_row.selected_value
        # Test si déjà utilisé par un stage
        # lecture de la table codes_stage
        liste = app_tables.codes_stages.search()
        liste_presence_qcm = []
        key_searched = str(qcm_row["qcm_nb"])   # je recherche ce qcm
        #alert(key_searched)
        for stage in liste:
            dico_qcm = stage['droit_qcm']
            # si ce qcm est dans ce stage, je sauve le stage dans une liste
            test = None
            test = dico_qcm.get(key_searched)
            if test is not None:
                liste_presence_qcm.append(stage["code"])
        nb_stages_avec_qcm = len(liste_presence_qcm)
        if nb_stages_avec_qcm > 0:
            alert(f"Effacer ce QCM est impossible,\nCar {nb_stages_avec_qcm} stage(s) l'utilise(nt) !\nDétail:\n{liste_presence_qcm}")
            alert("Pour effacer ce QCM, il vous faut d'abord ne plus l'affecter à un stage.")
            from ..QCM_par_stage import QCM_par_stage
            open_form("QCM_par_stage")
        else: 
            # Confirmation par l'utilisateur
            r=alert("Confirmez l'effacement complet de ce QCM ?",dismissible=False,buttons=[("oui",True),("non",False)])
            if r :   # oui
                result = anvil.server.call("qcm_del", qcm_row)
                if result is not True:
                    alert("Effacement du Qcm non effectué !")
                    return
                else:
                    alert("Effacement du Qcm effectué !")      
            open_form("QCM_visu_modif_Main")
            
    def drop_down_menu_change(self, **event_args):
        """This method is called when an item is selected"""
        self.choix = self.drop_down_menu.selected_value

        if self.choix==0:   # "Créer un nouveau QCM standard"
            self.drop_down_menu.visible = False
            self.check_box_examen.checked = False
            self.button_test.visible = False
            self.creation()
        if self.choix==1:   # "Créer un nouveau QCM exam"
            self.drop_down_menu.visible = False
            self.check_box_examen.checked = True
            self.button_test.visible = False
            self.creation()   
        if self.choix==2:    # "Modif un QCM existant":
            self.drop_down_qcm_row.visible = True
            self.drop_down_menu.visible = False
            self.button_del.visible = False
        if self.choix==3:    # "Effacer un QCM"
            self.drop_down_qcm_row.selected_value = None # initialiser le drop down choix du qcm
            self.drop_down_qcm_row.visible = True        #             le rendre visible             
            self.drop_down_menu.visible = False
            self.column_panel_creation_qcm.visible = False
            self.column_panel_exam.visible = False
            self.button_del.visible = True
            self.drop_down_qcm_row.placeholder = "QCM à Effacer"
        if self.choix==4:    # "Affecter un QCM à un stage":
            from ..QCM_par_stage import QCM_par_stage
            open_form("QCM_par_stage")


    def check_box_examen_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.check_box_examen.checked is True:
            
            r=alert("Ce Qcm sera basé sur d'autres Qcm !",dismissible=False,buttons=[("oui",True),("non",False)])
            if not r :   # non
                self.check_box_examen.checked = False
                return
        alert("Validez les caractéristiques de ce QCM examen !")
        self.column_panel_question.visible = False
        self.button_valid.visible = True

    def creation_question_click(self, **event_args):
        """This method is called when the button is clicked"""
        global liste
        nb_questions = len(liste)
        from ..QCM_visu_creation_html import QCM_visu_creation_html
        open_form('QCM_visu_creation_html', self.drop_down_qcm_row.selected_value, nb_questions)




 
    

   


    
   
    

    

    

 
 
        
        