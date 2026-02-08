from ._anvil_designer import Diplomes_nbTemplate
from anvil import *
import anvil.server
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
        #self.label_total.visible = False
        #self.label_total_txt.visible = False
        now=French_zone.french_zone_time()   # now est le jour/h actuelle (datetime object)
        now=now.date()                       # extraction de la date, format yyyy-mm-dd
        self.date_picker_to.date = now
        self.date_fin = now

        # Drop down codes Centres
        self.drop_down_lieux.items = [(r['lieu'], r) for r in app_tables.lieux.search()]

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.display()

    def button_pdf_click(self, **event_args):
        # ---- garde-fous ----
        if not self.date_deb or not self.date_fin:
            AlertHTML.error("Erreur :", "Choisis d'abord une date de début et une date de fin.")
            return

        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :", "La date de fin est inférieure à la date de début !")
            return

        # ---- 1) récupérer + grouper ----
        grouped, total_global = self._get_diplomes_grouped_by_centre(self.date_deb, self.date_fin)

        if total_global == 0:
            AlertHTML.error("Info :", "Aucun diplôme édité sur cette période.")
            return

        # ---- 2) construire HTML + CSS ----
        periode_txt = f"du {self.date_deb.strftime('%d/%m/%Y')} au {self.date_fin.strftime('%d/%m/%Y')}"
        print_date = French_zone.french_zone_time().strftime("%d/%m/%Y à %H:%M")

        css = self._pdf_css()

        body_html = []
        centres = sorted(grouped.keys(), key=lambda s: (s or "").lower())

        for idx, centre_name in enumerate(centres):
            data = grouped[centre_name]
            stages = data["stages"]
            total_centre = data["total"]

            # Titre
            title = f"Nb d'attestations éditées pour {centre_name}"
            title_safe = self._esc(title)
            # Centre
            centre_name_safe = self._esc(centre_name)
            # Sous titre
            subtitle = f"{periode_txt}"
            subtitle_safe = self._esc(subtitle)


            body_html.append(f"""
                <section class="centre-section">
                <h1 class="doc-title">{title_safe}</h1>
                <h2 class="doc-subtitle">{subtitle_safe}</h2>
    
                <div class="section-visible-title">
                    <div class="centre">{centre_name_safe}</div>
                    <div class="periode">{self._esc(periode_txt)}</div>
                </div>
    
                <table class="tbl">
                    <thead>
                    <tr>
                        <th>Date début</th>
                        <th>N° PV</th>
                        <th>Stage</th>
                        <th class="num">Diplômes</th>
                    </tr>
                    </thead>
                    <tbody>
            """)

            for st in stages:
                date_debut = st.get("date_debut_txt", "")
                num_pv = st.get("num_pv_txt", "")
                code_txt = st.get("code_txt", "")
                nb = st.get("nb", 0)

                body_html.append(f"""
                    <tr>
                    <td>{self._esc(date_debut)}</td>
                    <td>{self._esc(num_pv)}</td>
                    <td>{self._esc(code_txt)}</td>
                    <td class="num">{int(nb) if nb else 0}</td>
                    </tr>
                """)

            body_html.append(f"""
                    </tbody>
                </table>
    
                <div class="total-centre">
                    Total {centre_name_safe} : <b>{int(total_centre) if total_centre else 0}</b>
                </div>
                </section>
            """)

            if idx < len(centres) - 1:
                body_html.append('<div class="page-break"></div>')

        # ------------------------------------------------------------
        # Page récap finale
        # ------------------------------------------------------------
        body_html.append('<div class="page-break"></div>')

        # En-têtes (pour le header WeasyPrint via string-set)
        recap_title = self._esc("Récapitulatif par centre")
        recap_subtitle = self._esc(f"{periode_txt}")

        body_html.append(f"""
            <section class="centre-section">
              <h1 class="doc-title">{recap_title}</h1>
              <h2 class="doc-subtitle">{recap_subtitle}</h2>

              <div class="section-visible-title">
                <div class="centre">Récapitulatif</div>
                <div class="periode">{self._esc(periode_txt)}</div>
              </div>

              <table class="tbl recap">
                <thead>
                  <tr>
                    <th>Centre</th>
                    <th class="num">Diplômes</th>
                  </tr>
                </thead>
                <tbody>
        """)

        # Dernière page Recap / Lignes par centre (dans le même ordre que ton tri)
        for centre_name in centres:
            total_centre = grouped[centre_name]["total"]
            body_html.append(f"""
                <tr>
                  <td>{self._esc(centre_name)}</td>
                  <td class="num">{int(total_centre) if total_centre else 0}</td>
                </tr>
            """)

        # Trait + cumul
        body_html.append(f"""
                </tbody>
              </table>

              <div class="recap-sep"></div>

              <div class="total-global">
                Total global sur la période ({self._esc(periode_txt)}) : <b>{int(total_global)}</b>
              </div>
            </section>
        """)


        html_doc = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Diplômes édités</title>
        </head>
        <body>
            <span class="print-date">Imprimé le {self._esc(print_date)}</span>
            {''.join(body_html)}
        </body>
        </html>
        """
    
        # ---- 3) génération uplink + download ----
        filename = f"diplomes_{self.date_deb.strftime('%Y%m%d')}_{self.date_fin.strftime('%Y%m%d')}.pdf"
    
        with anvil.server.no_loading_indicator:
            pdf_media = anvil.server.call("render_pdf", html_doc, css, filename)
    
        if pdf_media:
            anvil.media.download(pdf_media)
        else:
            alert("Erreur lors de la génération du PDF")

        
    def drop_down_lieux_change(self, **event_args):
        """This method is called when an item is selected"""
        self.centre_formation_row = self.drop_down_lieux.selected_value
        self.date_picker_from.visible= True
        self.date_picker_to.visible= True
        try:  # si on met à None le centre de formation
            self.centre_formation_nom = self.centre_formation_row['lieu']
            self.label_result.text = f"Nb de diplômes édités pour {self.centre_formation_nom}"
            self.display()
        except:
            self.data_grid_1.visible = False
            self.label_total_txt.visible = False
            
    def date_picker_from_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        self.date_deb = self.date_picker_from.date
        
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :","La date de fin est inférieure à la date de début !")
            self.date_picker_from.focus()
        self.date_picker_to.visible = True
        self.repeating_panel_1.visible = False
        

    def date_picker_to_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        self.date_fin = self.date_picker_to.date
        
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :","La date de fin est inférieure à la date de début !")
            self.date_picker_to.focus()
        self.repeating_panel_1.visible = False
    
    def display(self):
        # search de tous les stages existants et affichage
        liste0 = []
        liste0 = app_tables.stages.search(
            tables.order_by("num_pv", ascending=True),
            nb_stagiaires_diplomes=q.not_(0),
        )

        liste1=[]
        nb_diplomes = 0
        for stage in liste0:
            if stage['nb_stagiaires_diplomes'] is not None:
                try:  # si les dates sont exactes
                    if stage['date_debut'] >= self.date_deb and stage['date_debut'] <= self.date_fin :
                        if stage['lieu'] ==self.centre_formation_row:
                            liste1.append(stage)
                            nb_diplomes = nb_diplomes + stage['nb_stagiaires_diplomes']
                            self.label_result.text = f"Nb de diplômes édités pour {self.centre_formation_nom}: {nb_diplomes}"
                            self.label_total_txt.text = f"Nb d'attestations pour {self.centre_formation_nom}: {nb_diplomes}"
                            self.label_total.visible = True
                            self.button_pdf.visible = True  
                except:
                    pass
        if nb_diplomes > 0:
            self.label_total_txt.visible = True
            self.date
            self.data_grid_1.visible = True
            self.repeating_panel_1.visible = True
            self.repeating_panel_1.items = liste1
        else:
            self.label_total_txt.visible = False
            self.data_grid_1.visible = False
                
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form('Main',99) 




    # =========================================================
    # Helpers
    # =========================================================
    def _esc(self, s):
        if s is None:
            return ""
        s = str(s)
        return (s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))
    
    def _get_diplomes_grouped_by_centre(self, date_deb, date_fin):
        """
        Retour:
          grouped = {
            "AMS": {"stages":[...], "total": 12},
            "MUC": {"stages":[...], "total": 5},
            ...
          }
          total_global = 17
        """

        # Requête côté tables (on limite déjà aux stages avec nb != 0)
        # On filtre les dates ensuite en Python (fiable, sans surprise)
        rows = app_tables.stages.search(
            tables.order_by("date_debut", ascending=True),
            nb_stagiaires_diplomes=q.not_(0),
        )

        grouped = {}
        total_global = 0

        for stage in rows:
            nb = stage['nb_stagiaires_diplomes'] or 0
            if nb == 0:
                continue

            d = stage['date_debut']
            if not d:
                continue

            if d < date_deb or d > date_fin:
                continue

            lieu_row = stage['lieu']
            centre_name = (lieu_row['lieu'] if lieu_row else "Centre inconnu") or "Centre inconnu"

            if centre_name not in grouped:
                grouped[centre_name] = {"stages": [], "total": 0}

            grouped[centre_name]["stages"].append({
                "date_debut_txt": d.strftime("%d/%m/%Y") if hasattr(d, "strftime") else str(d),
                "num_pv_txt": str(stage['num_pv'] or ""),
                "code_txt": str(stage.get('code_txt', "") or ""),
                "nb": int(nb),
            })

            grouped[centre_name]["total"] += int(nb)
            total_global += int(nb)

        # tri interne par date + num pv (utile si tu veux stable)
        for centre_name in grouped:
            grouped[centre_name]["stages"].sort(
                key=lambda x: (x["date_debut_txt"], x["num_pv_txt"])
            )

        return grouped, total_global

    def _pdf_css(self):
        return """
        @page {
            size: A4;
            margin: 1.8cm 1.6cm 2.0cm 1.6cm;

            @top-right {
                content: counter(page) " / " counter(pages);
                font-size: 9pt;
            }

            @top-center {
                content: string(title) "\\A" string(subtitle);
                white-space: pre;
                font-size: 11pt;
                font-weight: bold;
                text-align: center;
                padding-bottom: 2mm;
                border-bottom: 1px solid #888;
            }

            @bottom-center {
                content: string(printdate);
                font-size: 9pt;
            }
        }

        body {
            font-family: DejaVu Sans, sans-serif;
            font-size: 10.5pt;
            line-height: 1.35;
        }

        /* Variables invisibles pour WeasyPrint */
        h1.doc-title { string-set: title content(); display:block; height:0; overflow:hidden; margin:0; }
        h2.doc-subtitle { string-set: subtitle content(); display:block; height:0; overflow:hidden; margin:0; }
        span.print-date { string-set: printdate content(); display:block; height:0; overflow:hidden; }

        .section-visible-title {
            margin: 10pt 0 8pt 0;
        }
        .section-visible-title .centre {
            font-size: 14pt;
            font-weight: 800;
        }
        .section-visible-title .periode {
            font-size: 10pt;
            opacity: 0.9;
        }

        table.tbl {
            width: 100%;
            border-collapse: collapse;
            margin-top: 6pt;
        }
        table.tbl th, table.tbl td {
            border: 1px solid #bbb;
            padding: 5pt 6pt;
            vertical-align: top;
        }
        table.tbl th {
            font-weight: 700;
        }
        td.num, th.num {
            text-align: right;
            width: 12%;
            white-space: nowrap;
        }

        .total-centre {
            margin-top: 8pt;
            text-align: right;
            font-size: 11pt;
        }

        .total-global {
            margin-top: 14pt;
            padding-top: 8pt;
            border-top: 2px solid #000;
            text-align: right;
            font-size: 12pt;
        }

        .page-break {
            page-break-after: always;
        }
      

        table.tbl.recap td, table.tbl.recap th {
            font-size: 11pt;
        }

        .recap-sep {
            margin: 12pt 0 8pt 0;
        border-top: 2px solid #000;
        }
        
        .total-global {
            margin-top: 0;
        padding-top: 0;
        border-top: 0;
        text-align: right;
        font-size: 12pt;
        }

        """

   

