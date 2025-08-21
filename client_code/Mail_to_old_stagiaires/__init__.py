from ._anvil_designer import Mail_to_old_stagiairesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


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

    def button_tri_mail_click(self, **event_args):
        """This method is called when the button is clicked"""
        # lecture de toute la table old_stagiaires sur le mail
        self.liste_old_stagiaires = app_tables.stagiaires_histo.search(
                                                                    tables.order_by("mail", ascending=True),
                                                                     )
        self.label_nb_rows.text = str(len(self.liste_old_stagiaires))
        self.repeating_panel_1.items = self.liste_old_stagiaires

    def button_tri_nom_click(self, **event_args):
        """This method is called when the button is clicked"""
        # lecture de toute la table old_stagiaires sur le mail
        self.liste_old_stagiaires = app_tables.stagiaires_histo.search(
            tables.order_by("nom", ascending=True),
        )
        self.label_nb_rows.text = str(len(self.liste_old_stagiaires))
        self.repeating_panel_1.items = self.liste_old_stagiaires

   
    

 
