from ._anvil_designer import Stage_suivi_histogramsTemplate
from anvil import *

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import plotly.graph_objects as go
import anvil.server

from plotly import graph_objects as go
#from anvil_extras.PageBreak import PageBreak
from ...PageBreak import PageBreak

# AFFICHAGE D'un plot histogramme // RESULTATS pour 1 question fermée du formulaire de suivi
# APPELE PAR LA FORM 'STAGE_SATISF_Statistics' par add component:
#   (  self.column_panel_content.add_component(Stage_suivi_histograms(qt,r0,r1,r2,r3,r4,r5)) )


class Stage_suivi_histograms(Stage_suivi_histogramsTemplate):
    def __init__(self, qt, r0, r1, r2, r3, r4, r5, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        data = [r0, r1, r2, r3, r4, r5]  # axe des y
        listx = [0, 1, 2, 3, 4, 5]  # axe des x
        # texte à afficher ds les barres
        t0 = f"{r0} rép."
        t1 = f"{r1} rép."
        t2 = f"{r2} rép."
        t3 = f"{r3} rép."
        t4 = f"{r4} rép."
        t5 = f"{r5} rép."

        # Plot some data
        self.plot_1.data = [
            go.Bar(
                x=listx,
                y=data,
                # marker=dict(color="rgb(16, 32, 77)" ),    # couleur de toutes les barres
                marker=dict(
                    color=("red", "orangered", "orange", "greenyellow", "lime", "green")
                ),  # couleurs css de chaque barre ( https://lucidar.me/fr/web-dev/css-color-list/ )
                text=[t0, t1, t2, t3, t4, t5],
            )  # texte ds les barres
        ]

        # Configure the plot layout
        titre = qt
        self.plot_1.layout = {
            #'title': titre,    # titre du graphique
            "title": {
                "text": titre,
            },
            "title_font_color": "darkblue",
            "title_font_size": 16,
            "title_font_family": "Arial, bold",
            "xaxis": {
                "title": "(0:Très insatisfait à 5:Très satisfait)",
            },
            "yaxis": {
                "title": "Nb de réponses",
                "visible": False,  # Montre l'axe y et son titre  !!
                "tickmode": 1,  # de 1 en 1
            },
            "plot_bgcolor": "lightgrey",  # Couleur de fond personnalisée
            "showlegend": False,  # True pour montrer la légende (false par défaut voir l'init)
            "displayModeBar": False,  # Cache la barre des outils
        }

    def form_show(self, **event_args):
        """This method is called when the Image is shown on the screen"""
        self.add_component(PageBreak())  # st de page à chaque histogramme
        self.add_component(PageBreak(margin_top=24, border="1px dashed #ccc"))