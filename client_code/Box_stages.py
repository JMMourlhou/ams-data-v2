from ._anvil_designer import Box_stagesTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.tables.query as q

class Box_stages(Box_stagesTemplate):
    def __init__(self, stagiaire_row, stage, **properties):
        # Set Form properties and Data Bindings.

        # Any code you write here will run before the form opens.
        self.init_components(**properties)
        self.code_fi = None
        self.stagiaire_row = stagiaire_row
        self.stage = stage
        self.pour_stage = None   # le tuteur travaillera pour quel stage

        # Initialisation Drop down des stages que prendra en charge le Tuteur
        self.drop_down_fi.items = [(
                                    r['code_txt']+" / "+str(r['date_debut'])+" / "+str(r['numero']), r) for r in app_tables.stages.search(
                                    tables.order_by("numero", ascending=False),
                                    numero = q.less_than(900)
                                   )]

    def drop_down_fi_change(self, **event_args):
        """This method is called when an item is selected"""
        row = self.drop_down_fi.selected_value
        self.pour_stage = row['numero']
        self.button_ok.visible = True

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.remove_from_parent()

    def button_ok_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_annuler.visible = False
        #                                            row stagiaire        numero     code_fi     origine      stage pour lequel travaille le tuteur       
        txt_msg = anvil.server.call("add_stagiaire", self.stagiaire_row, self.stage,  'NO',   "bt_recherche", self.pour_stage)
        alert(txt_msg)
        open_form('Recherche_stagiaire_v2', self.stage)  # réouvre la forme mère pour mettre à jour l'affichage de l'histo
