from ._anvil_designer import PlotTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from plotly import (
    graph_objects as go,
)  # AFFICHAGE DES RESULTATS de plusieurs tests sur 1 QCM


class Plot(PlotTemplate):
    def __init__(
        self, user, nb, next_qcm=True, legend=False, **properties
    ):  # le nb vient de temp3 ds user (à cause du qcm BNSSA tiré de plusieurs qcm)
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # lecture du qcm description
        qcm_n = app_tables.qcm_description.get(qcm_nb=nb)
        min_rep = qcm_n["taux_success"]  # INT       ex : min = 75 %

        # lecture table qcm result, création de la liste des qcm de ce stagiaire pour 1 QCM
        infos_plot = ""  # Texte affiché en self.rich_text_infos_plot
        listx_int = []  # liste nb de fois qcm effectué         (1,    2,   3,  ...)
        listx_str = []  # liste nb de fois, mais en str pour affichage de x
        listy = []  # liste du résultat obtenu àch passage  (10%, 25%, 35%, ...)
        list_min = []
        liste_date_short = []
        liste_date_long = []

        cpt = 0
        if user:
            qcm_rows = (
                app_tables.qcm_result.search(  # permet la boucle sur les qcm passés
                    user_qcm=user, qcm_number=qcm_n
                )
            )
            nb_qcm_passe = len(qcm_rows)
            #print("nb de qcm", nb_qcm_passe)

        else:
            print("plot: user non trouvé")
            return

        for q in qcm_rows:
            cpt += 1
            listx_int.append(cpt)  # x INT
            listx_str.append(str(cpt))  # x STR
            listy.append(q["p100_sur_nb_rep"])  # y INT  Résultat du qcm
            list_min.append(
                min_rep
            )  # INT       ex : min = 75 %    pour dessiner la ligne horizontale du mini recqui
            liste_date_short.append(str(q["time"].strftime("%d/%m")))
            liste_date_long.append(
                str(q["time"].strftime("%d/%m/%Y, %Hh%M"))
            )  # 1 seul qcm, j'affiche les détails du timing

        
        #print(str(liste_date_short[nb_qcm_passe - 1]))

        #print("x int  ", listx_int)
        #print("x text ", listx_str)
        #print("y", listy)
        #print(list_min)

        # Plot some data     SI PLUSIEURS QCM EFFECTUES j'affiche la ligne des résultats, avec la ligne de mini recquis
        if len(qcm_rows) > 1:
            title = f"{nb_qcm_passe}ème test, QCM '{qcm_n['destination']}'"
            self.plot_1.data = [
                go.Scatter(x=listx_int, y=listy, marker=dict(color="rgb(16, 32, 77)")),
                go.Scatter(  # la ligne du mini recquis
                    x=listx_int,
                    y=list_min,
                    marker=dict(color="rgb(204, 0, 0)"),
                    mode="lines",
                    line=dict(dash="dash"),
                ),
            ]
        else:  # 1 SEUL QCM : Pie
            date_qcm = str(liste_date_long[nb_qcm_passe - 1])
            # title = f"QCM {qcm_n['destination']} du {date_qcm}, de {user['email']}"
            title = f"QCM {qcm_n['destination']} du {date_qcm}"
            colors = ["green", "red"]  # couleurs pour chaque tranche
            labels = ["% Bonnes réponses", "Erreurs"]  # Les étiquettes correspondantes
            listy_pour1qcm = [listy[0], 100 - listy[0]]
            if listy[0] >= 75:
                title_pie = "Réussite"
            else:
                title_pie = "Echec"

            self.plot_1.data = [
                go.Pie(
                    values=listy_pour1qcm,
                    labels=labels,
                    hole=0.4,
                    title=title_pie,
                    marker_colors=colors,
                )
            ]

        # Configure the plot layout
        if len(qcm_rows) > 1:  # Plusieurs passages
            self.plot_1.layout = {
                "displayModeBar": True,  # False: n'affiche que qd passe au dessus
                "modeBarButtonsToRemove": ["zoomIn2d", "zoomOut2d", "pan2d"],
                "title": title,
                "xaxis": {
                    "title": title,
                    "visible": False,  # Masque l'axe X et son titre  !!
                },
                "yaxis": dict(range=[0, 100]),
                "yaxis": {
                    "title": title,
                    "visible": True,  # Montre l'axe y et son titre  !!
                },
                "plot_bgcolor": "lightblue",  # Couleur de fond personnalisée
                "showlegend": False,  # True pour montrer la légende (false par défaut voir l'init)
            }
        else:  # 1 seul QCM: Pie, je n'affiche pas les axes
            self.plot_1.layout = {
                "displayModeBar": True,  # False: n'affiche que qd passe au dessus
                "modeBarButtonsToRemove": ["zoomIn2d", "zoomOut2d", "pan2d"],
                "title": title,
                "xaxis": {
                    "title": title,
                    "visible": False,  # Masque l'axe X et son titre  !!
                },
                "yaxis": {
                    "title": title,
                    "visible": True,  # Masque l'axe y et son titre  !!
                },
                "plot_bgcolor": "red",  # Couleur de fond personnalisée
            }

        self.plot_1.layout.yaxis.title = "% réponses ok - " + user["email"]
        # self.plot_1.layout.title.fontsize = 5
        date_deb = liste_date_short[0]  # dernière date
        date_fin = liste_date_short[nb_qcm_passe - 1]  # derniere date
        if len(qcm_rows) > 1:
            self.plot_1.layout.annotations = [
                dict(
                    text=date_deb,  # flèche commentaire
                    x=1,
                    xref="x",
                    y=0,
                    yref="y",
                    showarrow=True,  # Montre lea flèche :True
                    arrowhead=15,
                    ax=0,
                    ay=-20,
                    color="white",
                    fontsize=12,
                ),
                dict(
                    text=date_fin,  # flèche commentaire
                    x=nb_qcm_passe,
                    xref="x",
                    y=0,
                    yref="y",
                    showarrow=True,
                    arrowhead=15,
                    ax=0,  # 0
                    ay=-20,  # -20
                    color="white",
                    fontsize=12,
                ),
            ]
        """
             -------------------------------------------------------------------------------------------------------
                               AFFICHAGE DU RICH TEXT INFOS AU DESSUS DU PLOT
             ------------------------------------------------------------------------------------------------------                         
        """
        # print("+++++++++++++++++++ dernier résultat listy[nb_qcm_passe-1]: ", listy[nb_qcm_passe-1])
        # print("+++++++++++++++++++ mini recquis listy[nb_qcm_passe-1]: ", list_min[nb_qcm_passe-1])
        if (
            listy[nb_qcm_passe - 1] >= list_min[nb_qcm_passe - 1]
        ):  # si dernier résultat >= mini recquis
            infos_plot = f"**Réussite au QCM** {qcm_n['destination']} !" + "\n"
        else:
            infos_plot = f"**Echec au QCM** {qcm_n['destination']} !" + "\n"
        infos_plot = infos_plot + f"Le {liste_date_long[nb_qcm_passe-1]}" + "\n"
        infos_plot = (
            infos_plot + f"De **{user['prenom']} {user['nom']}**" + "\n\n"
        )  # NOM Prénom en Gras puis 2 st de ligne
        infos_plot = infos_plot + f"**{user['email']}**" + "\n\n"  # Mail
        infos_plot = (
            infos_plot + f"{listy[nb_qcm_passe-1]} % de réponses exactes" + "\n"
        )
        infos_plot = (
            infos_plot + f"(Minimum requis: {list_min[nb_qcm_passe-1]} %)" + "\n"
        )
        self.rich_text_infos_plot.content = infos_plot

        """
             -------------------------------------------------------------------------------------------------------
                            AFFICHAGE DU RICH TEXT NEXT QCM AU DESSOUS DU PLOT
                            (Si next_qcm = True, si vient d'un test qcm
                            Si next_qcm = False, vient d'un affichage en historique, pas de commentaires en dessous)
             ------------------------------------------------------------------------------------------------------                         
        """
        if next_qcm is True:
            # Lecture de la ligne du qcm descro pour déterminer si next plot ds table qcm descro:
            intitul_next_qcm = ""
            qcm_actuel_row = app_tables.qcm_description.get(qcm_nb=nb)
            if qcm_actuel_row:
                if qcm_actuel_row["next_qcm"]:
                    next_qcm_row = app_tables.qcm_description.get(
                        qcm_nb=qcm_actuel_row["next_qcm"]
                    )
                    if next_qcm_row:
                        intitul_next_qcm = next_qcm_row["destination"]
                        self.column_panel_2.visible = True

            if (
                listy[nb_qcm_passe - 1] >= list_min[nb_qcm_passe - 1]
            ):  # si dernier résultat >= mini recquis
                next_plot = (
                    f"**Vous ouvrez vos droits au QCM {intitul_next_qcm}**" + "\n\n"
                )
                next_plot = next_plot + "Bonne préparation !"
            else:
                next_plot = (
                    "Vous devez d'abord réussir ce QCM pour ouvrir vos droits au prochain :"
                    + "\n"
                )
                next_plot = next_plot + intitul_next_qcm + "\n \n"
                next_plot = next_plot + "On ne lâche rien ! \n"
            self.rich_text_next_qcm.content = next_plot

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .Main import Main
        open_form("Main", 99)

    def plot_1_click(self, points, **event_args):
        """This method is called when a data point is clicked."""
        print("download")
        # anvil.media.download(self.plot_1)
