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

        now = French_zone.french_zone_time()
        now = now.date()

        # Période par défaut : du 01/01 de l'année courante à aujourd'hui
        self.date_deb = now.replace(month=1, day=1)
        self.date_fin = now

        self.date_picker_from.date = self.date_deb
        self.date_picker_to.date = self.date_fin

        # --------------------------------------- Drop down Centres
        self.TOUS_CENTRES_VALUE = "__TOUS_LES_CENTRES__"

        # Par défaut
        self.tous_les_centres = True
        self.centre_formation_row = None
        self.centre_formation_nom = "Tous les centres"

        centres = app_tables.lieux.search(
            tables.order_by("lieu", ascending=True)
        )

        self.drop_down_lieux.items = (
            [("Tous les centres", self.TOUS_CENTRES_VALUE)]
            + [(r["lieu"], r) for r in centres]
        )

        #self.drop_down_lieux.selected_value = self.TOUS_CENTRES_VALUE
        # --------------------------------------- fin     Drop down Centres

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
    
        selected = self.drop_down_lieux.selected_value
    
        self.date_picker_from.visible = True
        self.date_picker_to.visible = True
        self.button_validation.visible = True
    
        # On efface l'ancien résultat affiché, car le filtre a changé
        #self.repeating_panel_1.visible = False
        self.repeating_panel_1.items = []
        self.data_grid_1.visible = False
        self.label_total_txt.visible = False
        self.button_pdf.visible = False
        self.button_xls.visible = False
    
        if selected == self.TOUS_CENTRES_VALUE:
            self.tous_les_centres = True
            self.centre_formation_row = None
            self.centre_formation_nom = "Tous les centres"
            self.flow_panel_2.visible = True
    
            self.label_result.text = "Critère sélectionné : tous les centres"
            return
    
        if selected is None:
            self.tous_les_centres = False
            self.centre_formation_row = None
            self.centre_formation_nom = None
    
            self.label_result.text = "Sélectionne un centre, puis clique sur Validation."
            return
    
        self.tous_les_centres = False
        self.centre_formation_row = selected
        self.centre_formation_nom = selected["lieu"]
    
        self.label_result.text = f"Critère sélectionné : {self.centre_formation_nom}"
            
    def date_picker_from_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        self.date_deb = self.date_picker_from.date
        
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :","La date de fin est inférieure à la date de début !")
            self.date_picker_from.focus()
        self.date_picker_to.visible = True
        self.column_panel_3.visible = False
        self.button_pdf.visible = False
        self.button_xls.visible = False
        self.label_total_txt.visible = False
        
    def date_picker_to_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.button_validation.visible = True   
        self.date_fin = self.date_picker_to.date
        
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :","La date de fin est inférieure à la date de début !")
            self.date_picker_to.focus()
        self.column_panel_3.visible = False
        self.button_pdf.visible = False
        self.button_xls.visible = False
        self.label_total_txt.visible = False
    
    def display(self):
        # Search de tous les stages existants, triés par numéro de PV
        liste0 = app_tables.stages.search(
            tables.order_by("num_pv", ascending=True),
            nb_stagiaires_diplomes=q.not_(0),
        )
    
        liste1 = []
        nb_diplomes = 0
    
        for stage in liste0:
            nb_stage = stage["nb_stagiaires_diplomes"] or 0
    
            if nb_stage == 0:
                continue
    
            date_debut = stage["date_debut"]
    
            if not date_debut:
                continue
    
            if not self.date_deb or not self.date_fin:
                continue
    
            if date_debut < self.date_deb or date_debut > self.date_fin:
                continue
    
            # Cas 1 : tous les centres
            if self.tous_les_centres:
                liste1.append(stage)
                nb_diplomes += nb_stage
                continue
    
            # Cas 2 : un centre précis
            if stage["lieu"] == self.centre_formation_row:
                liste1.append(stage)
                nb_diplomes += nb_stage
    
        if nb_diplomes > 0:
            if self.tous_les_centres:
                self.label_result.text = f"Nb de diplômes édités pour tous les centres : {nb_diplomes}"
                self.label_total_txt.text = f"Nb d'attestations pour tous les centres : {nb_diplomes}"
            else:
                self.label_result.text = f"Nb de diplômes édités pour {self.centre_formation_nom} : {nb_diplomes}"
                self.label_total_txt.text = f"Nb d'attestations pour {self.centre_formation_nom} : {nb_diplomes}"
    
            self.label_total_txt.visible = True
            self.data_grid_1.visible = True
            self.button_pdf.visible = True
            self.button_xls.visible = True
            self.repeating_panel_1.visible = True
            self.column_panel_3.visible = True
    
            # Liste déjà triée par num_pv grâce au search initial
            self.repeating_panel_1.items = liste1
    
        else:
            if self.tous_les_centres:
                self.label_result.text = "Aucun diplôme édité pour tous les centres sur cette période."
            else:
                self.label_result.text = f"Aucun diplôme édité pour {self.centre_formation_nom} sur cette période."
    
            self.label_total_txt.visible = False
            self.data_grid_1.visible = False
            self.button_pdf.visible = False
            self.button_xls.visible = False
            self.column_panel_3.visible = False
            self.repeating_panel_1.items = []
            self.label_total_txt.visible = False
                
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
    
        Les lignes sont triées par numéro de PV.
        """
    
        # Requête triée par numéro de PV
        rows = app_tables.stages.search(
            tables.order_by("num_pv", ascending=True),
            nb_stagiaires_diplomes=q.not_(0),
        )
    
        grouped = {}
        total_global = 0
    
        for stage in rows:
            nb = stage["nb_stagiaires_diplomes"] or 0
            if nb == 0:
                continue
    
            d = stage["date_debut"]
            if not d:
                continue
    
            if d < date_deb or d > date_fin:
                continue
    
            # Si un centre précis est sélectionné, on filtre ici
            if not self.tous_les_centres:
                if stage["lieu"] != self.centre_formation_row:
                    continue
    
            lieu_row = stage["lieu"]
            centre_name = (lieu_row["lieu"] if lieu_row else "Centre inconnu") or "Centre inconnu"
    
            if centre_name not in grouped:
                grouped[centre_name] = {"stages": [], "total": 0}
    
            grouped[centre_name]["stages"].append({
                "date_debut_txt": d.strftime("%d/%m/%Y") if hasattr(d, "strftime") else str(d),
                "num_pv_txt": str(stage["num_pv"] or ""),
                "code_txt": str(stage.get("code_txt", "") or ""),
                "nb": int(nb),
                "num_pv_sort": stage["num_pv"] or 0,
            })
    
            grouped[centre_name]["total"] += int(nb)
            total_global += int(nb)
    
        # Tri interne de chaque centre par numéro de PV
        for centre_name in grouped:
            grouped[centre_name]["stages"].sort(
                key=lambda x: x["num_pv_sort"]
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

    
    def button_xls_click(self, **event_args):
        """This method is called when the button is clicked"""
        if not self.date_deb or not self.date_fin:
            AlertHTML.error("Erreur :", "Choisis d'abord une date de début et une date de fin.")
            return
    
        if self.date_fin < self.date_deb:
            AlertHTML.error("Erreur :", "La date de fin est inférieure à la date de début !")
            return
    
        grouped, total_global = self._get_diplomes_grouped_by_centre(
            self.date_deb,
            self.date_fin
        )
    
        if total_global == 0:
            AlertHTML.error("Info :", "Aucun diplôme édité sur cette période.")
            return
    
        date_deb_txt = self.date_deb.strftime("%d/%m/%Y")
        date_fin_txt = self.date_fin.strftime("%d/%m/%Y")
    
        with anvil.server.no_loading_indicator:
            media_file, file_xls_name, message = anvil.server.call(
                "export_diplomes_nb_xls",
                grouped,
                total_global,
                date_deb_txt,
                date_fin_txt
            )
    
        if media_file:
            anvil.media.download(media_file)
        else:
            alert("Erreur lors de la génération du fichier Excel")

   

