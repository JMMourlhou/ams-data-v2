import anvil.email
from anvil.tables import app_tables
import anvil.server
from anvil.pdf import PDFRenderer

import time   # Pour calculer le tps de traitement
from datetime import datetime  # pour mettre la date et heure ds nomde fichier pdf (temporaire pour test)
from pytz import timezone      # 

import html, re, unicodedata  # POur génération du HTML 

"""
    quality :
    "original": All images will be embedded at original resolution. Output file can be very large.
    "screen": Low-resolution output similar to the Acrobat Distiller “Screen Optimized” setting.
    "printer": Output similar to the Acrobat Distiller “Print Optimized” setting.
    "prepress": Output similar to Acrobat Distiller “Prepress Optimized” setting.
 ** "default": Output intended to be useful across a wide variety of uses, possibly at the expense of a larger output file.
    """
# Calculer la taille du file et ajuster la qualité (screen : pas assez bon)

"""----------------------------------------------------------------------------------------------------------
                   BG task    Formulaire de SATISFACTION  Génération du PDF et sauvegarde en table stage
   ---------------------------------------------------------------------------------------------------------
"""
@anvil.server.background_task
def generate_satisf_results(stage_num, type, row):
    start = time.time()   # pour calcul du tpsde traitement (environ 25 sec)
    now_utc = datetime.now(timezone('UTC'))
    date_time = now_utc.astimezone(timezone('Europe/Paris')) # initialisation of the date & time of writing

    pdf_object = PDFRenderer(page_size ='A4',
                            filename = f"Enquete_satisf_{type}_{stage_num}_{date_time}.pdf",
                            #filename = f"Enquete_satisf_{type}_{stage_num}.pdf",
                            landscape = False,
                            margins = {'top': 0.3, 'bottom': 0.1, 'left': 0.2, 'right': 0.2},  #  cm
                            scale = 1.0,                                                       
                            quality = "screen"      
                            ).render_form('Stage_satisf_statistics',True,row)    # True: pdf mode, j'efface le bt return et passe le row du stage qui avait été sélectionné
   
    # sauvegarde du résultat de l'enquete media
    row.update(satis_pdf = pdf_object) 
    end = time.time()
    print("Temps de traitement: ", end-start)
    
# A FAIRE APPELER from client side
@anvil.server.callable
def run_bg_task_satisf(stage_num, type, row):
    task = anvil.server.launch_background_task('generate_satisf_results',stage_num, type, row)
    return task


"""----------------------------------------------------------------------------------------------------------
                   BG task    Formulaire de SUIVI Génération du PDF et sauvegarde en table stage
    ---------------------------------------------------------------------------------------------------------
"""
@anvil.server.background_task
def generate_suivi_results(type_suivi, stage_num, type, row):
    start = time.time()   # pour calcul du tpsde traitement (environ 25 se)
    now_utc = datetime.now(timezone('UTC'))
    date_time = now_utc.astimezone(timezone('Europe/Paris')) # initialisation of the date & time of writing

    pdf_object = PDFRenderer(page_size ='A4',
                            filename = f"Enquete_satisf_{type}_{stage_num}_{date_time}.pdf",
                            #filename = f"Enquete_satisf_{type}_{stage_num}.pdf",
                            landscape = False,
                            margins = {'top': 0.3, 'bottom': 0.1, 'left': 0.2, 'right': 0.2},  #  cm
                            scale = 1.0,                                                       
                            quality = "screen"      
                            ).render_form('Stage_suivi_results',type_suivi, True,row)    # True: pdf mode, j'efface le bt return et passe le row du stage qui avait été sélectionné
   
    # sauvegarde du résultat de l'enquete media
    row.update(suivi_pdf = pdf_object) 
    end = time.time()
    print("Temps de traitement: ", end-start)
    
# A FAIRE APPELER from client side
@anvil.server.callable
def run_bg_task_suivi(type_suivi, stage_num, type, row):
    task = anvil.server.launch_background_task('generate_suivi_results', type_suivi, stage_num, type, row)
    return task



#import html, re, unicodedata

# ------------------ Helpers ------------------

def _esc(s):
    return html.escape(s or "")

def _clean_text(s):
    """Nettoie les caractères de contrôle et normalise Unicode."""
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFC", s)
    # retire les contrôles hors \n \t
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", s)
    return s

def _fmt_tel(t):
    if isinstance(t, str) and len(t) == 10 and t.isdigit():
        return f"{t[0:2]}-{t[2:4]}-{t[4:6]}-{t[6:8]}-{t[8:10]}"
    return _esc(t or "")

def _user_from_email(email_or_obj):
    """Retourne (prenom, nom, tel, email_str) depuis 'users'."""
    email_str, tel = None, None
    if isinstance(email_or_obj, dict):
        email_str = email_or_obj.get("email")
        tel = email_or_obj.get("tel")
    else:
        email_str = email_or_obj
    u = app_tables.users.get(email=email_str) if email_str else None
    prenom = (u and u.get("prenom")) or ""
    nom = (u and (u.get("nom") or u.get("name"))) or ""
    # priorité au tel issu de la ligne users si dispo
    tel = (u and (u.get("tel") or (u.get("user_email") or {}).get("tel"))) or tel
    return prenom, nom, _fmt_tel(tel), email_str or ""

def _render_open_blocks(rep_ouv: dict) -> str:
    """
    rep_ouv est supposé être { 'Question label'|id : ['réponse 1', 'réponse 2' ...], ... }
    """
    blocks = []
    for q, vals in (rep_ouv or {}).items():
        q_label = _esc(_clean_text(q))
        lis = "".join(f"<li>{_esc(_clean_text(v))}</li>" for v in (vals or []))
        answer_html = f"<ul class='qa-list'>{lis}</ul>" if lis else "<div class='qa-empty'>—</div>"
        blocks.append(f"""
          <section class="qa-block">
            <div class="qa-title">{q_label}</div>
            {answer_html}
          </section>
        """)
    return "".join(blocks)

def _render_ratings_table(rep_ferm: dict) -> str:
    """
    rep_ferm est supposé être { 'Intitulé note' : 0..5 | 'texte', ... }
    On rend un tableau simple, proche du PDF d'exemple (libellé + valeur).
    """
    if not rep_ferm:
        return ""
    rows = []
    for label, val in rep_ferm.items():
        label = _esc(_clean_text(label))
        value_txt = _esc(_clean_text(val))
        # barre visuelle (optionnelle si val numérique)
        bar = ""
        try:
            n = int(str(val).strip())
            n_clamped = max(0, min(5, n))
            bar = f"<div class='bar'><div class='bar-fill' style='width:{n_clamped*20}%'>&nbsp;</div></div>"
        except Exception:
            pass
        rows.append(f"""
          <tr>
            <td class="r-label">{label}</td>
            <td class="r-value">{value_txt}{bar}</td>
          </tr>
        """)
    return f"""
      <table class="rating-table">
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    """

def _css_enquete():
    # CSS dédiée au rendu "résultats de formulaires de suivi"
    return """
@page {
  size: A4;
  margin: 14mm 14mm 16mm 14mm;
  @bottom-center {
    content: "Page " counter(page) " / " counter(pages);
    font-size: 9pt;
    color: #0047ab;
  }
}
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 11pt; color: #111; }

.header { text-align: center; margin-bottom: 8px; }
.header h1 { margin: 0; font-size: 16pt; color: #0047ab; }
.header h2 { margin: 2px 0 0 0; font-size: 12pt; color: #222; }

.stage-meta { text-align:center; font-size:10pt; color:#444; margin: 2px 0 10px; }

.person-card {
  border: 1px solid #e2e6ef; border-radius: 6px;
  padding: 10px 12px; margin: 10px 0;
  page-break-inside: avoid; background: #fff;
}
.person-head { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:baseline; margin-bottom:8px; }
.person-name { font-weight:700; color:#0047ab; font-size:12.5pt; }
.person-tel { font-size:10.5pt; color:#333; }

.qa-block { margin: 8px 0; }
.qa-title {
  font-weight: 700; color: #222; background: #f3f6ff;
  border-left: 3px solid #0047ab; padding: 6px 8px; border-radius: 4px;
  font-size: 10.5pt;
}
.qa-list { margin: 6px 0 0 18px; }
.qa-empty { margin: 6px 0 0 6px; color:#777; }

.rating-table { width:100%; border-collapse:collapse; margin-top:8px; }
.rating-table td { border: 1px solid #d7dbe6; padding: 6px; vertical-align: middle; }
.rating-table td.r-label { width: 70%; }
.rating-table td.r-value { width: 30%; white-space: nowrap; }

.bar { height: 6px; margin-top: 4px; border-radius: 3px; background: #eef2ff; overflow: hidden; }
.bar-fill { height: 100%; background: #0047ab; }

.small-note { font-size:9pt; color:#666; text-align:right; margin-top:2px; }

.hr { height:0; border:0; border-top:1px solid #e6eaf2; margin: 10px 0; }
"""

# ------------------ Générateur principal ------------------

@anvil.server.callable
def enquete_suivi_pdf_gen(stage_row, role="S"):
    """
    Produit un PDF 'Résultat Formulaires de suivi de stages' pour un stage donné.
    - stage_row: ligne du stage (contient p.ex. 'numero', 'code', 'date_debut')
    - role: 'S' (Stagiaire) ou 'T' (Tuteur), par défaut 'S'
    """
    # Métadonnées stage
    stage_num = str(stage_row.get('numero') if hasattr(stage_row, 'get') else stage_row['numero'])
    stage_code = (stage_row.get('code') or {}).get('code') if hasattr(stage_row, 'get') else stage_row['code']['code']
    date_txt = stage_row.get('date_debut').strftime("%Y-%m-%d")  # ton PDF montre AAAA-MM-JJ
    titre_haut = "Résultat Formulaires de suivi de stages"
    sous_titre = f"Stagiaires du Stage n°{stage_num} {stage_code} du {date_txt}"

    # Récupération des formulaires de ce stage + rôle
    forms = app_tables.stage_suivi.search(stage_num_txt=stage_num, user_role=role)

    # Grouper par email stagiaire
    grouped = {}  # email -> [formulaires]
    for f in forms:
        mel = f.get('user_email')
        if isinstance(mel, dict):
            mel = mel.get('email')
        if mel:
            grouped.setdefault(mel, []).append(f)

    # Construire les blocs stagiaires
    people_blocks = []
    for mel, flist in grouped.items():
        prenom, nom, tel_fmt, email_str = _user_from_email(mel)
        # Si plusieurs formulaires par personne : on concatène les Q/R
        rep_ouv_all, rep_ferm_all = {}, {}
        for formulaire in flist:
            # Fusion Q ouvertes
            for q, vals in (formulaire.get('rep_dico_rep_ouv') or {}).items():
                rep_ouv_all.setdefault(q, [])
                rep_ouv_all[q].extend(vals or [])
            # Fusion "fermées"
            for q, v in (formulaire.get('rep_dico_rep_ferm') or {}).items():
                # si plusieurs valeurs, on garde la dernière (ou tu peux agréger autrement)
                rep_ferm_all[q] = v

        open_html = _render_open_blocks(rep_ouv_all)
        ratings_html = _render_ratings_table(rep_ferm_all)

        people_blocks.append(f"""
        <section class="person-card">
          <div class="person-head">
            <div class="person-name">{_esc(prenom)} {_esc(nom)}</div>
            <div class="person-tel">{_esc(tel_fmt or '')}</div>
          </div>
          {open_html}
          {ratings_html}
        </section>
        """)

    # HTML complet
    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{_esc(titre_haut)}</title>
    <style>{_css_enquete()}</style>
  </head>
  <body>
    <header class="header">
      <h1>{_esc(titre_haut)}</h1>
      <h2>{_esc(sous_titre)}</h2>
    </header>
    <div class="stage-meta">Généré automatiquement depuis les formulaires de suivi</div>
    {''.join(people_blocks) if people_blocks else '<p>Aucune réponse trouvée.</p>'}
    <div class="small-note">Rôle: {_esc(role)}</div>
  </body>
</html>
"""
    filename = f"Enquete_satisf_{_esc(stage_code)}_{_esc(stage_num)}.pdf"
    return anvil.server.call("render_pdf", html_doc, filename)
