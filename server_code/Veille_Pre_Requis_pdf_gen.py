import anvil.secrets
# -*- coding: utf-8 -*-
"""
Module serveur Anvil : veille_pr_requis

Génère un PDF d'état des documents requis pour tous les formateurs AMS.

Deux modes :
    - "compact"       : les formateurs s'enchaînent sans saut de page forcé.
    - "une_page"      : chaque nouveau formateur commence sur une nouvelle page.

Le PDF est produit par l'Uplink Pi5 :
    anvil.server.call("render_pdf", html_doc, css, filename)
"""

from anvil.tables import app_tables
import anvil.server
import anvil.tables as tables
from . import Formatage_date   # Module serveur: formatter la date 0102030405 en 01-02-03-04-05
import html
from datetime import date, datetime

try:
    from zoneinfo import ZoneInfo
    TZ_PARIS = ZoneInfo("Europe/Paris")
except Exception:
    TZ_PARIS = None


# Alerte si un document expire dans moins de 60 jours.
NB_JOURS_ALERTE_EXPIRATION = 60


# =============================================================================
# Helpers généraux
# =============================================================================

def _esc(value):
    """Échappement HTML."""
    if value is None:
        return ""
    return html.escape(str(value))


def _row_value(row, column, default=None):
    """
    Lecture tolérante d'une colonne d'une Row Anvil.
    """
    if row is None:
        return default

    try:
        value = row[column]
        return default if value is None else value
    except Exception:
        pass

    try:
        value = row.get(column)
        return default if value is None else value
    except Exception:
        return default


def _today_paris():
    now = datetime.now(TZ_PARIS) if TZ_PARIS else datetime.now()
    return now.date()


def _now_paris():
    return datetime.now(TZ_PARIS) if TZ_PARIS else datetime.now()


def _as_date(value):
    """
    Transforme date/datetime en date.
    Renvoie None si la valeur n'est pas exploitable.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return None


def _format_date(value):
    d = _as_date(value)
    return d.strftime("%d/%m/%Y") if d else ""


def _safe_text(value):
    return "" if value is None else str(value).strip()


# =============================================================================
# Lecture / classification des prérequis
# =============================================================================

def _classer_document(pr, today):
    """
    Retourne un dictionnaire normalisé décrivant l'état d'un prérequis.

    Statuts :
        ok
        missing
        expired
        expiring_soon
        no_expiry_date
    """
    item_requis = _row_value(pr, "item_requis")
    doc1 = _row_value(pr, "doc1")
    date_expiration_raw = _row_value(pr, "date_expiration")
    date_expiration = _as_date(date_expiration_raw)

    est_expirable = bool(_row_value(item_requis, "Expiration", False))

    if doc1 is None:
        status = "missing"
        status_label = "À renseigner"

    elif est_expirable:
        if date_expiration is None:
            status = "no_expiry_date"
            status_label = "Date d'expiration à renseigner"
        elif today > date_expiration:
            status = "expired"
            status_label = "Expiré"
        else:
            jours_restants = (date_expiration - today).days

            if jours_restants < NB_JOURS_ALERTE_EXPIRATION:
                status = "expiring_soon"

                if jours_restants == 0:
                    status_label = "Expire aujourd'hui"
                elif jours_restants == 1:
                    status_label = "Expire dans 1 jour"
                else:
                    status_label = f"Expire dans {jours_restants} jours"
            else:
                status = "ok"
                status_label = "À jour"

    else:
        status = "ok"
        status_label = "À jour"

    return {
        "libelle": _safe_text(_row_value(pr, "requis_txt")),
        "status": status,
        "status_label": status_label,
        "expiration": date_expiration,
        "est_expirable": est_expirable,
    }


def _documents_formateur(personne, today, mode, stage=None):
    """
    Lit les prérequis du formateur ou du stagiaire et conserve uniquement ceux liés
    à un stage de type 'F'.

    Les documents internes AMS sont séparés des documents externes.
    """
    internes = []
    externes = []        

    liste_pre_requis = app_tables.pre_requis_stagiaire.search(
        tables.order_by("requis_txt", ascending=True),
        stagiaire_email=personne
    )

    for pr in liste_pre_requis:
        stage_row = _row_value(pr, "stage_num")

        # Même filtre fonctionnel que dans le script de test :
        # uniquement les prérequis rattachés à un stage de type formateur si mode "compacte" ou "une_page". (docs formateurs)
        #if mode != "stage" and _row_value(stage_row, "type_stage") != "F":
        #    continue
            
        # TEST si  docs du stage qund vient d'un stage pas d'une recherche perso
        #if stage_row != stage and mode != "perso" and mode != "compact" and mode != "une_page":
        if stage_row != stage and mode == "stage" :
            continue

        # Test: Si mode "perso" (vient de recherche), si le doc n'appartient pas à un stage "stage avec PR" on passe
        print(f"debug: stage sans pr: {stage_row['stage_sans_pre_requis']}")
        if stage_row["stage_sans_pre_requis"] is not True:
            continue
            
        doc = _classer_document(pr, today)

        item_requis = _row_value(pr, "item_requis")
        doc_interne_ams = _row_value(item_requis, "doc_interne_ams")

        if doc_interne_ams is True:
            internes.append(doc)
        else:
            # Comme dans le script de test :
            # False OU None => document externe AMS.
            externes.append(doc)

    return internes, externes


def _stats_documents(internes, externes):
    docs = internes + externes

    stats = {
        "total": len(docs),
        "ok": 0,
        "missing": 0,
        "expired": 0,
        "expiring_soon": 0,
        "no_expiry_date": 0,
    }

    for doc in docs:
        status = doc["status"]
        if status in stats:
            stats[status] += 1

    stats["anomalies"] = (
        stats["missing"]
        + stats["expired"]
        + stats["no_expiry_date"]
    )

    return stats


# =============================================================================
# Génération HTML
# =============================================================================

def _status_icon(status):
    return {
        "ok": "✓",
        "missing": "!",
        "expired": "!",
        "expiring_soon": "!",
        "no_expiry_date": "!",
    }.get(status, "")


def _render_document_rows(documents):
    if not documents:
        return """
        <tr class="empty-row">
            <td colspan="3">Aucun document dans cette catégorie.</td>
        </tr>
        """

    rows = []

    for doc in documents:
        expiration_txt = ""

        if doc["est_expirable"]:
            if doc["expiration"] is not None:
                expiration_txt = _format_date(doc["expiration"])
            elif doc["status"] == "no_expiry_date":
                expiration_txt = "Non renseignée"
        else:
            expiration_txt = "—"

        rows.append(f"""
        <tr class="doc-row status-{_esc(doc['status'])}">
            <td class="doc-name">{_esc(doc['libelle'])}</td>
            <td class="doc-status">
                <span class="status-badge">
                    <span class="status-icon">{_status_icon(doc['status'])}</span>
                    {_esc(doc['status_label'])}
                </span>
            </td>
            <td class="doc-date">{_esc(expiration_txt)}</td>
        </tr>
        """)

    return "".join(rows)


def _render_document_table(titre, documents, classe):
    return f"""
    <div class="doc-section {classe}">
        <div class="doc-section-title">{_esc(titre)}</div>
        <table class="doc-table">
            <colgroup>
                <col class="col-doc">
                <col class="col-status">
                <col class="col-date">
            </colgroup>
            <thead>
                <tr>
                    <th>Document requis</th>
                    <th>État</th>
                    <th>Expiration</th>
                </tr>
            </thead>
            <tbody>
                {_render_document_rows(documents)}
            </tbody>
        </table>
    </div>
    """


def _render_formateur(formateur, internes, externes, index, mode):
    nom = _safe_text(_row_value(formateur, "nom"))
    prenom = _safe_text(_row_value(formateur, "prenom"))
    email = _safe_text(_row_value(formateur, "email"))
    tel = Formatage_date.telephone_fr(_row_value(formateur, "tel"))   # Formatage tel 0102030405 en 01-02-03-04-05 à partie du module serveur Formatage
    print(f"Nom: {nom} tel:{tel} mode:{mode}")
    stats = _stats_documents(internes, externes)

    if stats["total"] == 0:
        resume_class = "resume-warning"
        resume_txt = "Ce formateur ne fait plus parti de l'équipe actuelle."
    elif stats["anomalies"] == 0:
        resume_class = "resume-ok"
        resume_txt = f"Tous les documents sont à jour ({stats['ok']}/{stats['total']})."
    else:
        resume_class = "resume-alert"
        details = []

        if stats["missing"]:
            details.append(f"{stats['missing']} à renseigner")
        if stats["expired"]:
            details.append(f"{stats['expired']} expiré(s)")
        if stats["no_expiry_date"]:
            details.append(
                f"{stats['no_expiry_date']} date(s) d'expiration manquante(s)"
            )

        resume_txt = (
            f"{stats['anomalies']} anomalie(s) sur {stats['total']} document(s) : "
            + ", ".join(details)
            + "."
        )

    return f"""
    <section class="person-card mode-{_esc(mode)}">
        <div class="person-header">
            <div class="person-number">{index}</div>
            <div class="person-identity">
                <div class="person-name">{_esc(nom)} {_esc(prenom)}</div>
                <div class="person-email">{_esc(email)}</div>
                <div class="person-tel">{_esc(tel)}</div>
            </div>
            <div class="person-summary {resume_class}">
                {_esc(resume_txt)}
            </div>
        </div>

        {_render_document_table(
            "Documents requis internes à AMS",
            internes,
            "internal-docs"
        )}

        {_render_document_table(
            "Documents requis externes à AMS",
            externes,
            "external-docs"
        )}
    </section>
    """


def _css(mode):
    """
    CSS commun + comportement de pagination selon le mode.
    """
    if mode == "une_page":
        pagination_css = """
        .person-card {
            break-before: page;
            page-break-before: always;
        }

        .person-card:first-of-type {
            break-before: auto;
            page-break-before: auto;
        }
        """
    else:
        # Compact :
        # aucun saut de page forcé entre deux personnes.
        pagination_css = """
        .person-card {
            break-before: auto;
            page-break-before: auto;
        }
        """

    return f"""
@page {{
    size: A4;
    margin: 19mm 12mm 16mm 12mm;

    @top-center {{
        content: element(doc-header);
    }}

    @top-right {{
        content: element(doc-meta);
    }}

    @bottom-center {{
        content: "Page " counter(page) " / " counter(pages);
        font-size: 8pt;
        color: #5f6368;
    }}
}}

* {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

html, body {{
    margin: 0;
    padding: 0;
    font-family: "DejaVu Sans", Arial, sans-serif;
    font-size: 9.5pt;
    color: #202124;
}}

.page-header {{
    position: running(doc-header);
    text-align: center;
    padding-top: 1mm;
}}

.page-header .title {{
    color: #0b4f82;
    font-size: 11pt;
    font-weight: 700;
    line-height: 1.2;
}}

.page-header .subtitle {{
    color: #4b5563;
    font-size: 8pt;
    font-weight: 600;
    margin-top: 1mm;
}}

.page-header-right {{
    position: running(doc-meta);
    text-align: right;
    padding-top: 1mm;
    color: #6b7280;
    font-size: 6.5pt;
    font-weight: 600;
}}

.report-summary {{
    border: 1px solid #cfd8e3;
    background: #f7f9fc;
    border-radius: 6px;
    padding: 7px 9px;
    margin: 0 0 8px 0;
    font-size: 8.7pt;
}}

.report-summary strong {{
    color: #0b4f82;
}}

.summary-expiry-missing {{
    color: #a02d24;
    font-weight: 700;
}}

.person-card {{
    border: 1px solid #cfd8e3;
    border-radius: 6px;
    padding: 8px;
    margin: 0 0 9px 0;
    background: #ffffff;
}}

{pagination_css}

.person-header {{
    display: grid;
    grid-template-columns: 8mm 1fr;
    column-gap: 8px;
    row-gap: 2px;
    align-items: center;
    border-bottom: 1px solid #dbe2ea;
    padding-bottom: 6px;
    margin-bottom: 7px;
}}

.person-number {{
    width: 7mm;
    height: 7mm;
    line-height: 7mm;
    text-align: center;
    border-radius: 50%;
    background: #0b4f82;
    color: white;
    font-weight: 700;
    font-size: 8pt;
}}

.person-name {{
    font-size: 11pt;
    font-weight: 700;
    color: #0b4f82;
}}

.person-email {{
    margin-top: 1px;
    color: #6b7280;
    font-size: 7.8pt;
}}

.person-tel {{
    margin-top: 1px;
    color: #6b7280;
    font-size: 7.8pt;
}}


.person-summary {{
    grid-column: 2;
    justify-self: start;
    max-width: none;
    padding: 4px 6px;
    border-radius: 4px;
    font-size: 7.8pt;
    font-weight: 700;
    text-align: left;
    white-space: nowrap;
}}

.resume-ok {{
    background: #e7f6ec;
    color: #236b3c;
}}

.resume-alert {{
    background: #fff0df;
    color: #8a4b08;
}}

.resume-warning {{
    background: #fff7d6;
    color: #725d00;
}}

.doc-section {{
    margin-top: 6px;
}}

.doc-section-title {{
    font-weight: 700;
    font-size: 8.8pt;
    color: #0b4f82;
    background: #eef5fb;
    border-left: 3px solid #0b4f82;
    padding: 4px 6px;
    margin-bottom: 3px;
}}

.external-docs .doc-section-title {{
    color: #5c456f;
    background: #f5f0f8;
    border-left-color: #7b5b91;
}}

.doc-table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 8.2pt;
}}

.doc-table col.col-doc {{
    width: 52%;
}}

.doc-table col.col-status {{
    width: 31%;
}}

.doc-table col.col-date {{
    width: 17%;
}}

.status-no_expiry_date .doc-status {{
    color: #725d00;
    background: #fff8dc;

    padding-left: 2px;
    font-size: 7.8pt;
}}

.status-no_expiry_date .status-icon {{
    width: 8px;
    margin-right: 1px;
}}

.doc-table th {{
    border: 1px solid #d9e0e7;
    background: #f7f8fa;
    color: #4b5563;
    padding: 3px 5px;
    font-size: 7.5pt;
    text-align: left;
}}

.doc-table td {{
    border: 1px solid #d9e0e7;
    padding: 3px 5px;
    vertical-align: middle;
}}

.doc-status,
.doc-date {{
    white-space: nowrap;
}}

.doc-date {{
    text-align: center;
}}

.status-badge {{
    display: inline-block;
    font-weight: 700;
}}

.doc-section {{
    break-inside: avoid;
    page-break-inside: avoid;
}}

.doc-section-title {{
    break-after: avoid;
    page-break-after: avoid;
}}

.doc-table {{
    break-inside: avoid;
    page-break-inside: avoid;
}}

.status-icon {{
    display: inline-block;
    width: 12px;
    text-align: center;
    margin-right: 2px;
}}

.status-ok .doc-status {{
    color: #236b3c;
    background: #f0f9f3;
}}

.status-missing .doc-status,
.status-expired .doc-status {{
    color: #a02d24;
    background: #fdecea;
}}

.status-expiring_soon .doc-status {{
    color: #8a4b08;
    background: #fff4e8;
}}

.status-no_expiry_date .doc-status {{
    color: #725d00;
    background: #fff8dc;
}}

.empty-row td {{
    text-align: center;
    color: #8a9099;
    font-style: italic;
    background: #fafafa;
}}

.mode-compact {{
    break-inside: avoid;
    page-break-inside: avoid;
}}

/*
En mode une_page on ne force pas break-inside: avoid :
si un formateur possède exceptionnellement trop de lignes pour tenir sur une
seule feuille A4, WeasyPrint peut poursuivre proprement sur la page suivante
au lieu de perdre/couper le contenu.
*/
.mode-une_page {{
    break-inside: auto;
    page-break-inside: auto;
}}
"""


# =============================================================================
# Générateur principal
# =============================================================================

@anvil.server.callable
def veille_pr_requis_pdf_gen(mode="compact", email=None, stage=None):  # stage: stage row
    """
    Génère l'état PDF des documents requis des formateurs oustagiaires d'1 stage AMS.
    email : provenance de recherche, envoi du mail du formateur 
    mode :
        "compact"  -> pas de saut de page forcé entre formateurs
        "une_page" -> chaque formateur commence sur une nouvelle page
        "perso"    -> un formateur (de recherche)
    """
    if mode not in ("compact", "une_page", "perso", "stage"):
        raise ValueError(
            "Mode PDF invalide. Utiliser 'compact', 'une_page', 'perso', 'stage'."
        )

    today = _today_paris()
    now = _now_paris()

    if mode == "compact" or mode == "une_page":
        liste = app_tables.users.search(
            tables.order_by("nom", ascending=True),
            tables.order_by("prenom", ascending=True),
            role="F"
        )
        title="État Docs requis: Formateurs d'AMSport."
    elif mode == "perso":
        personne = app_tables.users.get(email=email)
        if personne is None:
            raise ValueError(
                f"Aucun utilisateur trouvé avec l'adresse email : {email}"
            )
        liste = [personne]
        title=f"État Docs requis de {personne['nom']} {personne['prenom']} - AMSport."
    else: # mode="stage"
        liste = app_tables.stagiaires_inscrits.search(
            tables.order_by("name", ascending=True),
            tables.order_by("prenom", ascending=True),
            numero=stage['numero']
        )
        title=f"État Docs requis: Stage {stage['code_txt']} n° {stage['numero']} débuté le {stage['date_debut']}."
        print(f"mode {mode}, titre:{title}")
    people_blocks = []

    nb_formateurs = 0
    nb_formateurs_ok = 0
    nb_formateurs_anomalie = 0

    total_docs = 0
    total_missing = 0
    total_expired = 0
    total_no_expiry = 0

    for index, personne in enumerate(liste, start=1):
        # trouver le row table user ds table stgiaire insrit donc colonne 'user_email'
        if mode == "stage": # table stagiaire_insrit
            personne = personne['user_email']
            
        nb_formateurs += 1

        internes, externes = _documents_formateur(personne, today, mode, stage)
        stats = _stats_documents(internes, externes)

        total_docs += stats["total"]
        total_missing += stats["missing"]
        total_expired += stats["expired"]
        total_no_expiry += stats["no_expiry_date"]

        if stats["total"] > 0 and stats["anomalies"] == 0:
            nb_formateurs_ok += 1
        elif stats["anomalies"] > 0:
            nb_formateurs_anomalie += 1

        people_blocks.append(
            _render_formateur(
                personne,
                internes,
                externes,
                index,
                mode
            )
        )

    gen_txt = now.strftime("%d/%m/%Y %H:%M")
    date_fichier = now.strftime("%Y-%m-%d_%H-%M")

    if mode == "compact":
        mode_label = "Version compacte"
        filename = f"etat_documents_formateurs_AMS_compact_{date_fichier}.pdf"
    elif mode == "une_page":   # Tous formateurs, 1 page par formateur
        mode_label = "Un formateur par page"
        filename = f"etat_documents_formateurs_AMS_1page_{date_fichier}.pdf"
    else:
        mode_label = ""   # 1 seul formateur, lancé par recherche
        filename = f"etat_documents_formateurs_AMS_1page_{date_fichier}.pdf"

    total_anomalies = total_missing + total_expired + total_no_expiry

    if total_no_expiry > 0:
        texte_dates_manquantes = (
            f'<span class="summary-expiry-missing">'
            f'{total_no_expiry} date(s) d\'expiration manquante(s)'
            f'</span>'
        )
    else:
        texte_dates_manquantes = (
            f"{total_no_expiry} date(s) d'expiration manquante(s)"
        )
    if mode == "compact" or mode == "une_page" :
        summary_html = f"""
        <div class="report-summary">
            <strong>{nb_formateurs}</strong> formateur(s) enregistré(s) —
            <strong>{total_docs}</strong> document(s) contrôlé(s) —
            <strong>{nb_formateurs_ok}</strong> personne(s) entièrement à jour —
            <strong>{nb_formateurs_anomalie}</strong> personnes avec anomalie(s) —
            <strong>{total_anomalies}</strong> anomalie(s) au total
            ({total_missing} à renseigner, {total_expired} expiré(s),
            {texte_dates_manquantes}).
        </div>
        """
    else:  # mode "stage" pour stagiaires d'un stage
        summary_html = f"""
        <div class="report-summary">
            <strong>Rapport pour {nb_formateurs} personne(s) </strong> —
            <strong>{total_docs}</strong> document(s) contrôlé(s) —
            <strong>{total_anomalies}</strong> anomalie(s) au total
            ({total_missing} à renseigner, {total_expired} expiré(s),
            {texte_dates_manquantes}).
        </div>
        """

      
    html_doc = f"""<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
    <div class="page-header">
        <div class="title">{title}</div>
        <div class="subtitle">{_esc(mode_label)}</div>
    </div>

    <div class="page-header-right">
        Édité le {_esc(gen_txt)}
    </div>

    {summary_html}

    {''.join(people_blocks) if people_blocks else '<p>Aucun formateur trouvé.</p>'}
</body>
</html>
"""

    css = _css(mode)

    # Uplink Pi5 existant.
    return anvil.server.call(
        "render_pdf",
        html_doc,
        css,
        filename
    )
