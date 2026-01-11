from ._anvil_designer import Diplomes_nbTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from datetime import timedelta
from .. import French_zone   #pour tester la date de naissance
from ..AlertHTML import AlertHTML
from ..AlertConfirmHTML import AlertConfirmHTML


class Diplomes_nb(Diplomes_nbTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        now=French_zone.french_zone_time()   # now est le jour/h actuelle (datetime object)
        now=now.date()                       # extraction de la date, format yyyy-mm-dd
        self.date_picker_to.date = now
        self.date_fin = now

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.display()

    def button_pdf_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def date_picker_from_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        self.date_deb = self.date_picker_from.date
        print()
        print(f"Date_deb: {self.date_deb}")
        print(f"Date_fin: {self.date_fin}")
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :","La date de fin est inférieure à la date de début !")
            self.date_picker_from.focus()
        self.date_picker_to.visible = True
        self.column_panel_1.visible = False
        

    def date_picker_to_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        self.date_fin = self.date_picker_to.date
        print()
        print(f"Date_deb: {self.date_deb}")
        print(f"Date_fin: {self.date_fin}")
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :","La date de fin est inférieure à la date de début !")
            self.date_picker_to.focus()
        self.column_panel_1.visible = False
    
    def display(self):
        # search de tous les stages existants et affichage
        liste0 = []
        liste0 = app_tables.stages.search(
            tables.order_by("num_pv", ascending=True),
            nb_stagiaires_diplomes=q.not_(0),
        )
        print(f"nb stages liste0: {len(liste0)}")

        liste1=[]
        for stage in liste0:
            if stage['nb_stagiaires_diplomes'] is not None:
                alert()
                if stage['date_debut'] >= self.date_deb and stage['date_debut'] <= self.date_fin :
                    print(f"ajout: {stage['date_debut']}")
                    liste1.append(stage)
                    
        self.column_panel_1.visible = True
        self.repeating_panel_1.items = liste1

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 

