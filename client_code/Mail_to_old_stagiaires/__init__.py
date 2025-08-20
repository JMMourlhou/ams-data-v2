from ._anvil_designer import Mail_to_old_stagiairesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Mail_valideur  # pour button_export_xls_click
from .. import French_zone # POur acquisition de date et heure Francaise (Browser time)

class Mail_to_old_stagiaires(Mail_to_old_stagiairesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        #import anvil.js    # pour screen size
        from anvil.js import window # to gain access to the window object
        global screen_size
        screen_size = window.innerWidth
        print("screen: ", screen_size)
        if screen_size > 800:
            self.data_grid_1.rows_per_page = 7
            
        #lecture des lignes sélectionnées pour envoi
        nb_select = app_tables.stagiaires_histo.search(select=True)
        self.label_nb_select.text = len(nb_select)
        # lecture de tous les anciens stagiaires
        self.liste_old_stagiaires = app_tables.stagiaires_histo.search(
                                                                    tables.order_by("type_mail", ascending=True),
                                                                     )
        self.label_nb_rows.text = str(len(self.liste_old_stagiaires))
        self.repeating_panel_1.items = self.liste_old_stagiaires

    def button_mailing_click(self, **event_args):
        """This method is called when the button is clicked"""
        liste_email = []
        for stagiaire in self.liste_old_stagiaires:
            #lecture table user
            id = stagiaire.get_id()
            if stagiaire['select'] is True:
                liste_email.append((stagiaire["mail"], stagiaire["prenom"], id))
            
        # 'formul' indique l'origine, ici 'formulaire de satisfaction'
        open_form("Mail_subject_attach_txt",  liste_email, 'next_stages', True) # True, old stagiaires

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99)

    def button_comp_stagiaires_click(self, **event_args):
        """This method is called when the button is clicked"""
        # comparaison avec stgiares inscrits
        liste_actuelle = app_tables.stagiaires_inscrits.search()
        msg = f"Nb de stagiares inscrits: {len(liste_actuelle)}"
        alert(msg)
        nb = 0
        for stagiaire in liste_actuelle:
            exist = app_tables.stagiaires_histo.get(mail=stagiaire['user_email']['email'])
            if exist:
                nb += 1
                print(nb, stagiaire["name"], stagiaire["prenom"])
                #exist.delete()
        msg = f"Nb de doublons effacés: {nb}"
        alert(msg)

    def button_tri_nom_click(self, **event_args):
        """This method is called when the button is clicked"""
        # lecture de toute la table old_stagiaires sur le mail
        self.liste_old_stagiaires = app_tables.stagiaires_histo.search(
                                                                    tables.order_by("mail", ascending=True),
                                                                     )
        self.label_nb_rows.text = str(len(self.liste_old_stagiaires))
        self.repeating_panel_1.items = self.liste_old_stagiaires

    def button_valid_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_retour_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
        self.column_panel_add.visible = False
        self.button_valid.visible = False

    def button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.column_panel_add.visible = True

    def text_box_nom_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_valid.visible = True

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        if len(self.text_box_nom.text) < 3:
            alert("Le nom n'est pas assez long !")
            self.text_box_nom.focus()
            return
        if len(self.text_box_prenom.text) < 3:
            alert("Le prénom n'est pas assez long !")
            self.text_box_prenom.focus()
            return
        
        # Mail format validation
        self.mail = self.text_box_mail.text
        result = Mail_valideur.is_valid_email(self.mail)    # dans module Mail_valideur, fonction appelée 'is_valid_email'
        if result is False:
            alert("Le mail n'a pas le bon format !")
            self.text_box_mail.focus()
            return
        alert("ok")
        result = anvil.server.call("new_user",
                                   self.text_box_nom.text,
                                   self.text_box_prenom.text,
                                   self.text_box_tel.text,
                                   self.text_box_mail.text,
                                   signed_up = French_zone.french_zone_time(),  # importé en ht de ce script
                                  )
        if result is not None:
            alert(result)
        else:
            alert("Création effectuée !")