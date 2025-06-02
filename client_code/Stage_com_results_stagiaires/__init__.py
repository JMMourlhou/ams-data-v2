from ._anvil_designer import Stage_com_results_stagiairesTemplate
from .. import French_zone  # POur acquisition de date et heure Francaise (Browser time)
from anvil import *
import stripe.checkout

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


# Résultat des évaluation en comm pour une date précise 
class Stage_com_results_stagiaires(Stage_com_results_stagiairesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # Initialisation dropdown date
        liste_dates = []
        liste_initiale = app_tables.com_sum.search()
        for date_row in liste_initiale:
            if date_row["date"] not in liste_dates:
                liste_dates.append(date_row['date'])
        self.drop_down_date.items = liste_dates

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form("Main", 99)

    def drop_down_date_change(self, **event_args):
        """This method is called when an item is selected"""
        self.date_intervention = self.drop_down_date.selected_value        
        liste = app_tables.com_sum.search(tables.order_by("nom"),
                                                            date=self.date_intervention
                                                        )


        list1 = liste[0]   # extraction du premier item pour lire les questions
        self.label_1.text = list1['q1']
        self.label_2.text = list1['q2']
        self.label_3.text = list1['q3']
        self.label_4.text = list1['q4']
        self.label_5.text = list1['q5']
        self.label_6.text = list1['q6']
        self.label_7.text = list1['q7']
        self.label_8.text = list1['q8']
        self.label_9.text = list1['q9']
        self.label_10.text = list1['q10']
        
        self.repeating_panel_results.items = liste
        