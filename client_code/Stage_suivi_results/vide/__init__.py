from ._anvil_designer import videTemplate
from anvil import *
import anvil.server
#from anvil_extras.PageBreak import PageBreak
from ...PageBreak import PageBreak

# AFFICHAGE vide qd le tuteur a plusieurs stagiaires pour le formulaire de suivi
# APPELE PAR LA FORM 'S.ItemTemplate17' par add component:


class vide(videTemplate):
    def __init__(self, nom_tuteur, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.label_1.text = (f"Autre stagiaire de {nom_tuteur} :")
    

    def form_show(self, **event_args):
        self.add_component(PageBreak())  
        self.add_component(PageBreak(margin_top=24, border="1px dashed #ccc"))