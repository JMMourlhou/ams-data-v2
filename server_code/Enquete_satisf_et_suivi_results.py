from anvil.tables import app_tables
import anvil.server
import html, re, unicodedata  # POur génération du HTML 

# Génération de formulaires de suivi / stagiaires
#   à partir de HTML, CSS
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
    Accepte deux formes:
    A) { "1": ["Libellé", 4], "2": ["Libellé", 5], ... }  (comme dans ton PDF)
    B) { "Libellé": 4, "Libellé2": 5, ... }               (fallback)
    Rend un tableau 3 colonnes: n° | libellé | note (+barre)
    Coloration de ligne selon la note (0→5).
    """
    if not rep_ferm:
        return ""

    rows = []

    # Normalisation en liste de tuples (qnum, label, value)
    norm = []
    for k, v in rep_ferm.items():
        qnum = None
        label = ""
        value = v
        # Forme A : clé = numéro, valeur = [label, note]
        if (isinstance(v, (list, tuple)) and len(v) >= 2):
            qnum = str(k)
            label = str(v[0])
            value = v[1]
        else:
            # Forme B : clé = libellé, val = note
            label = str(k)

        # Valeur texte + entier (si possible)
        value_txt = str(value)
        score = None
        try:
            score = int(str(value).strip())
            score = max(0, min(5, score))
        except Exception:
            score = None

        norm.append((qnum, label, value_txt, score))

    # Tri croissant par n° si présent
    def _key(x):
        qnum = x[0]
        try:
            return (0, int(qnum))
        except:
            return (1, str(qnum) if qnum is not None else "~")
    norm.sort(key=_key)

    # Génération HTML
    for qnum, label, value_txt, score in norm:
        bar = ""
        if score is not None:
            bar = f"<div class='bar'><div class='bar-fill' style='width:{score*20}%'></div></div>"
        tr_class = f"score-{score}" if score is not None else ""
        rows.append(f"""
          <tr class="{tr_class}">
            <td class="qnum">{_esc(qnum) if qnum is not None else ""}</td>
            <td class="rlabel">{_esc(_clean_text(label))}</td>
            <td class="rval">{_esc(value_txt)}{bar}</td>
          </tr>
        """)

    return f"""
      <table class="rating-table">
        <colgroup>
          <col class="qnum"><col class="rlabel"><col class="rval">
        </colgroup>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    """


def _css_enquete():
    return """
@page {
  size: A4;
  /* marge haute augmentée pour accueillir l'en-tête répété */
  margin: 22mm 14mm 16mm 14mm;

  /* Pied de page (pagination) */
  @bottom-center {
    content: "Page " counter(page) " / " counter(pages);
    font-size: 9pt; color: #0047ab;
  }

  /* En-tête répété à chaque page */
  @top-center {
    content: element(doc-header);
  }
}

/* police & rendu print */
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 11pt; color: #111; }

/* ----- En-têtes ----- */
/* En-tête répété (police 12) */
.page-header {
  position: running(doc-header);
  text-align: center;
  padding-top: 2mm;
}
.page-header .h1, .page-header .h2 {
  margin: 0; font-size: 12pt; line-height: 1.2;
}
.page-header .h1 { color: #0047ab; font-weight: 700; }
.page-header .h2 { color: #222;  font-weight: 600; }

/* Grand en-tête de la 1re page (optionnel) */
.header { text-align: center; margin: 6px 0 8px; }
.header h1 { margin: 0; font-size: 16pt; color: #0047ab; }
.header h2 { margin: 2px 0 0 0; font-size: 12pt; color: #222; }

.stage-meta { text-align:center; font-size:10pt; color:#444; margin: 2px 0 10px; }

/* ----- Cartes personnes ----- */
.person-card {
  border: 1px solid #e2e6ef; border-radius: 6px;
  padding: 10px 12px; margin: 10px 0;
  page-break-inside: avoid; background: #fff;
}
.person-head { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:baseline; margin-bottom:8px; }
.person-name { font-weight:700; color:#0047ab; font-size:12.5pt; }
.person-tel { font-size:10.5pt; color:#333; }

/* ----- Questions ouvertes ----- */
.qa-block { margin: 8px 0; }
.qa-title {
  font-weight: 700; color: #222; background: #f3f6ff;
  border-left: 3px solid #0047ab; padding: 6px 8px; border-radius: 4px;
  font-size: 10.5pt;
}
.qa-list { margin: 6px 0 0 18px; }
.qa-empty { margin: 6px 0 0 6px; color:#777; }

/* ----- Questions fermées (notes) ----- */
.rating-table { width:100%; border-collapse:collapse; margin-top:8px; table-layout: fixed; }
.rating-table col.qnum   { width: 4ch; }         /* 1re colonne limitée à ~4 caractères */
.rating-table col.rlabel { width: auto; }
.rating-table col.rval   { width: 8ch; }         /* colonne note compacte */

.rating-table td { border: 1px solid #d7dbe6; padding: 6px; vertical-align: middle; }
.rating-table td.qnum   { text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rating-table td.rval   { text-align: center; white-space: nowrap; }
.rating-table td.rlabel { word-wrap: break-word; overflow-wrap: anywhere; }

/* Barre visuelle optionnelle sous la note */
.bar { height: 6px; margin-top: 4px; border-radius: 3px; background: #eef2ff; overflow: hidden; }
.bar-fill { height: 100%; background: #0047ab; }

/* Coloration de ligne en fonction de la note (0→5) */
tr.score-0 { background: #fbe9e9; }  /* Error */
tr.score-1 { background: #ffe5cc; }  /* Orange */
tr.score-2 { background: #fff2cc; }  /* Jaune Orange */
tr.score-3 { background: #e8f5e9; }  /* Vert Très Clair */
tr.score-4 { background: #dcedc8; }  /* Vert Clair */
tr.score-5 { background: #c8e6c9; }  /* Vert Foncé */

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

    <!-- En-tête répété à chaque page (police 12pt) -->
    <div class="page-header">
      <div class="h1">{_esc(titre_haut)}</div>
      <div class="h2">{_esc(sous_titre)}</div>
    </div>

    <!-- Grand en-tête de la 1re page (facultatif) -->
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
