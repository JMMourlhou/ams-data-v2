from ._anvil_designer import Evenements_types_MAJ_table_v2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Word_editor import Word_editor   # Word processor component inséré ds self.content_panel
from .one_event_type import one_event_type

# MAJ des types d'évènements, utilise Word_processor
class Evenements_types_MAJ_table_v2(Evenements_types_MAJ_table_v2Template):
    def __init__(self, **properties):  
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.text_box_1.placeholder = "Nom du nouveau type d'évenement"
        self.text_box_3.placeholder = "1er message ex: 'Nouvel xxx'"
        self.text_box_4.placeholder = "2eme message ex: 'Voir un xxx'"
        self.text_area_1.placeholder = "Texte initial"
        # search de tous les pré-requis existants et affichage
        liste_tous = app_tables.event_types.search(tables.order_by("code", ascending=True))
        self.nb = len(liste_tous)
        self.text_box_2.text = str(self.nb)  # le premier code commencant à 0, je n'ai pas à incrémenter += 1
        self.check_box_1.checked = False
        
        for row_event_type in liste_tous: 
            new_row = one_event_type(row_event_type)
            new_row.row_to_be_modified = None
            new_row.row_to_be_deleted = None
            new_row.set_event_handler('x-modif', self.modif)
            new_row.set_event_handler('x-del', self.delete)
            self.content_panel_events_rows.add_component(new_row)

    # ==========================================================================================================
    # Event raised: Changement un text box du row a été cliqué pour modif
    def modif(self, sender, **event_args):
        self.row = sender.row_to_be_modified
        self.sov_text_box_2 = self.row['code']
        self.text_box_1.text = self.row['type']
        self.text_box_2.text = self.row['code']
        self.text_box_3.text = self.row['msg_0']
        self.text_box_4.text = self.row['msg_1']
        self.check_box_1.checked = self.row['mot_clef_setup']
        
        self.column_panel_add_modif.visible = True
        self.call_word_editor(self.row['text_initial'], 'modif')
        
    """
    =============================================================================================================================================      CALL FOR THE WORD EDITOR
    """
    def call_word_editor(self, content_text_html, mode):
        # INSERTION TEXT-EDITOR form 'Word_editor'  (voir import)
        text_editor = Word_editor()
        text_editor.text = content_text_html   # .text: propriété crée ds la forme student_row (col de gauche ide anvil, 'Edit properties and event')
        text_editor.param1 = mode              # mode 'modif'
        text_editor.set_event_handler('x-fin_saisie', self.handle_click_fin_saisie)   # Qd bouton 'Fin' de 'Word_editor'form is clicked
        #text_editor.set_event_handler('x-timer_text_backup', self.timer_text_backup)   # Backup tous les 15 sec, timer_2 de la form Word_editor
        self.content_panel.add_component(text_editor)
    """
    =================================================================================================================================================================================
    """
    
    def delete(self, sender, **event_args):
        row = sender.row_to_be_deleted
        alert(row)
    
    # ------------------------------------------------Fonctions en CREATION d'un type d'évenement =================================================
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Parametres import Parametres
        open_form("Parametres")

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_add_modif.visible = True

    def button_valid_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Text_box_1 (type evnt) non vide
        if self.text_box_1.text == "" or len(self.text_box_1.text) < 5:
            alert("Entrez un type d'évenement clair (> à 5 caractères")
            self.text_box_1.focus()
            return
        # Text_box_2 (code) non vide
        if self.text_box_2.text == "" or int(self.text_box_2.text) < (self.nb):
            alert("Entrez un code valide !")
            self.text_box_2.focus()
            return

        # Text_box_3 (msg 0)non vide
        if self.text_box_3.text == "" or len(self.text_box_3.text) < 6:
            alert(
                "Entrez le message qui apparaîtra dans le menu ! (au moins 6 caractères)"
            )
            self.text_box_3.focus()
            return

        # Text_box_4 (msg 1)non vide
        if self.text_box_4.text == "" or len(self.text_box_4.text) < 6:
            alert(
                "Entrez le message qui apparaîtra dans le 2eme menu ! (au moins 6 caractères)"
            )
            self.text_box_4.focus()
            return

        # Code existant ?
        nb = int(self.text_box_2.text)
        row = app_tables.event_types.get(code=nb)
        if row:
            alert("Ce code est déjà pris !")
            self.text_box_2.focus()
            return

        r = alert(
            "Voulez-vous vraiment ajouter ce Type d'évenement ?",
            dismissible=False,
            buttons=[("oui", True), ("non", False)],
        )
        if r:  # oui
            nb = int(self.text_box_2.text)
            result = anvil.server.call(
                "add_type_evnt",
                self.text_box_1.text,  # type devnt
                nb,  # code (numérique)
                self.text_box_3.text,  # msg_1
                self.text_box_4.text,  # msg_2
                self.text_area_1.text,  # text_initial
                self.check_box_1.checked,  # mot clé daté ?  True/ False
            )
            if result is not True:
                alert("ERREUR, Ajout non effectué !")
                return
            alert("Création effectuée !")
        self.column_panel_add.visible = False
        open_form("Evenements_MAJ_table")

    # Fin des fonctions de créations d'un type d'évenemnt ==============================================

    

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def text_box_3_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True


    
    # ============================================================================================================
    # Event raised: BOUTON VALIDATION / Bt 'Fin' was clicked in Word_editor form (modif du text de base de l'évènement)
    def handle_click_fin_saisie(self, sender, **event_args):
        # sender.text contains the 'Word_editor'form's HTML text
        mode = sender.param1       # mode 'modif' /  'creation' 
        text = sender.text    # texte html de lévenement
        self.validation(text, mode)

    # mode= 'modif / 'creation'
    def validation(self, text, mode, **event_args):    
        """This method is called when the button is clicked"""

        # tests sur le code du type d'évenement -----------------------------    
        # Text_box_2 (code) vide ? 
        if self.text_box_2.text == "":
            alert("Entrez un code !")
            self.text_box_2.focus()
            return

        # Code existant en dehors de lui ?
        test = app_tables.event_types.search(code=int(self.text_box_2.text))
        
        alert(f"nb de rows existantes: {len(test)}")
        alert(f"actuel: {self.text_box_2.text}")
        alert(f"ancien: {str(self.sov_text_box_2)}")
        
        txt = str(self.text_box_2.text).strip()
        old = str(self.sov_text_box_2).strip()
        if len(test)==1 and txt != old:   # self.sov_text_box_2   est int
            alert("Ce code est déjà pris !")
            self.text_box_2.focus()
            return

        # je ne test pas le code 0 qui ne contient pas de texte dans les colonnes en dehors de code et msg1 
        if self.sov_text_box_2 != 0:   
            # Text_box_1 (type evnt) non vide
            if self.text_box_1.text == "" or len(self.text_box_1.text) < 5:
                alert("Entrez un type d'évenement clair (> à 5 caractères")
                self.text_box_1.focus()
                return    

            # Text_box_3 (msg 0)non vide  ------------------------------------------------------------
            if self.text_box_3.text == "" or len(self.text_box_3.text) < 6:
                alert("Entrez le message qui apparaîtra dans le 1er menu ! (au moins 6 caractères)")
                self.text_box_3.focus()
                return

            # Text_box_4 (msg 1)non vide
            if self.text_box_4.text == "" or len(self.text_box_4.text) < 6:
                alert("Entrez le message qui apparaîtra dans le 2eme menu ! (au moins 6 caractères)")
                self.text_box_4.focus()
                return   


        r=alert("Voulez-vous vraiment modifier ce type d'évenement ?",buttons=[("oui",True),("non",False)])
        if r :   # oui
            nb = int(self.text_box_2.text)
            result = anvil.server.call("modif_type_evnt", self.item, self.text_box_1.text,
                                       nb,
                                       self.text_box_3.text,
                                       self.text_box_4.text,
                                       text,
                                       self.check_box_1.checked               
                                      )
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert("Modification effectuée !")

        else:   # non
            pass
        open_form("Evenements_types_MAJ_table_v2")

       
