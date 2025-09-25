from anvil.tables import app_tables
import anvil.server
import html, re, unicodedata  # POur génération du HTML 
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_PARIS = ZoneInfo("Europe/Paris")
except Exception:
    TZ_PARIS = None

# Génération de formulaires de suivi des TUTEURS
#   à partir de HTML, CSS
# ------------------ Helpers ------------------
_qnum_re = re.compile(r'^\s*(\d+)\s*[\)\.\-:]?\s*(.*)$')

def _split_qnum_label(q):
    """Retourne (qnum, qlabel) en acceptant:
       - str: '1) Ton nom...'  -> ('1','Ton nom...')
       - dict: {'num':1,'label':'Ton nom...'} etc.
       - ou juste un libellé sans numéro.
    """
    if isinstance(q, dict):
        qnum = q.get('num') or q.get('numero') or q.get('qnum')
        qlabel = q.get('label') or q.get('libelle') or q.get('question') or ''
        return (str(qnum) if qnum is not None else None, _clean_text(qlabel))

    s = _clean_text(q)
    m = _qnum_re.match(s)
    if m:
        return m.group(1), m.group(2)
    return None, s

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


def _render_open_blocks(rep_ouv: dict) -> str:
    blocks = []
    # On normalise en liste pour trier
    items = []
    for k, vals in (rep_ouv or {}).items():
        qnum, qlabel = _split_qnum_label(k)
        items.append((qnum, qlabel, k, vals))

    # Tri : d’abord par numéro si dispo, sinon par libellé
    def sort_key(x):
        qnum, qlabel, _, _ = x
        try:
            return (0, int(qnum))
        except Exception:
            return (1, str(qlabel))

    items.sort(key=sort_key)

    # Génération HTML trié
    for qnum, qlabel, k, vals in items:
        answers = []
        if isinstance(vals, (list, tuple)):
            if len(vals) == 2 and isinstance(vals[0], str) and isinstance(vals[1], (list, tuple)):
                if not qlabel:
                    qlabel = vals[0]
                answers = list(vals[1])
            else:
                if (not qlabel) and vals and isinstance(vals[0], str):
                    first = vals[0].strip()
                    if first.endswith((':', '?')) or len(first) <= 80:
                        qlabel = first
                        answers = list(vals[1:])
                    else:
                        answers = list(vals)
                else:
                    answers = list(vals)
        else:
            answers = [str(vals)] if vals else []

        qlabel = _clean_text(qlabel or "")
        lis = "".join(f"<li>{_esc(_clean_text(v))}</li>" for v in answers)
        answer_html = f"<ul class='qa-list'>{lis}</ul>" if lis else "<div class='qa-empty'>—</div>"

        blocks.append(f"""
          <section class="qa-block">
            <div class="qa-title">
              <span class="qnum">{_esc(qnum) if qnum else ""}</span>
              <span class="qlabel">{_esc(qlabel)}</span>
            </div>
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


def _css():
    return """
@page {
  size: A4;
  margin: 18mm 14mm 16mm 14mm;
  @bottom-center { content: "Page " counter(page) " / " counter(pages); font-size: 9pt; color: #0047ab; }
  @top-center    { content: element(doc-header); }
  @top-right     { content: element(doc-meta); }   /* <- horodatage à droite */
}

/* Print */
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 11pt; color: #111; }

/* En-tête répété (centre) */
.page-header { position: running(doc-header); text-align: center; padding-top: 2mm; }
.page-header .h1, .page-header .h2 { margin: 0; font-size: 10pt; line-height: 1.2; }
.page-header .h1 { color: #0047ab; font-weight: 700; }
.page-header .h2 { color: #0047ab; font-weight: 600; }

/* En-tête répété (droite) */
.page-header-right {
  position: running(doc-meta);
  text-align: right;
  padding-top: 2mm;
  font-size: 6pt;
  color: #666;
  font-weight: 700
}

/* La fiche n'est pas coupée */
.person-card {
  border: 1px solid #e2e6ef; border-radius: 6px;
  padding: 10px 12px; margin: 10px 0;
  background: #fff;
  break-inside: avoid;           /* (= page-break-inside: avoid) */
  page-break-inside: avoid;
}

/* Saut AVANT chaque fiche sauf la première */
.person-card + .person-card {
  break-before: page;            /* (= page-break-before: always) */
  page-break-before: always;
}
.person-card:last-child {
  page-break-after: auto;     /* pas de page blanche finale */
}
.person-head { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:baseline; justify-content: center; margin-bottom:8px; }
.person-name { font-weight:700; color:#B3261E; font-size:12.5pt; }
.person-tel  { font-size:9pt; color:#B3261E; }

/* Ouvertes */
.qa-block { margin: 8px 0; break-inside: avoid; }
.qa-title {
  /* Grille 2 colonnes : n° étroit + libellé qui prend la place restante */
  display: grid;
  grid-template-columns: max-content 1fr;
  column-gap: 6px;
  align-items: center;

  font-weight: 700; color: #222;
  background: #f3f6ff;             /* fond bleu clair conservé */
  border-left: 3px solid #0047ab;
  padding: 6px 8px; border-radius: 4px;
  font-size: 10.5pt;
  width: 100%;
  box-sizing: border-box;
}
.qa-title .qnum {
  color: #0047ab;
  min-width: 2ch;
  text-align: right;
}
.qa-title .qlabel {
  min-width: 0;      /* permet le retour à la ligne si le libellé est long */
  white-space: normal;
  color: #0047ab;       /* <- même bleu que le numéro */
  font-weight: 700;     /* même emphase que le n° */
}

.qa-list { margin: 6px 0 0 18px; }
.qa-empty { margin: 6px 0 0 6px; color:#777; }

/* Fermées / notes */
.rating-table { width:100%; border-collapse:collapse; margin-top:8px; table-layout: fixed; }
.rating-table col.qnum   { width: 4ch; }
.rating-table col.rlabel { width: auto; }
.rating-table col.rval   { width: 8ch; }
.rating-table td { border:1px solid #d7dbe6; padding:6px; vertical-align:middle; }
.rating-table td.qnum { text-align:center; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rating-table td.rval { text-align:center; white-space:nowrap; }
.rating-table td.rlabel { word-wrap:break-word; overflow-wrap:anywhere; }

.bar { height:6px; margin-top:4px; border-radius:3px; background:#eef2ff; overflow:hidden; }
.bar-fill { height:100%; background:#0047ab; }

/* Couleurs selon note */
tr.score-0 { background:#B3261E; }
tr.score-1 { background:#FF7B22; }
tr.score-2 { background:#FFD707; }
tr.score-3 { background:#DDF9A5; }
tr.score-4 { background:#61D007; }
tr.score-5 { background:#00FF00; }

.small-note { font-size:9pt; color:#666; text-align:right; margin-top:2px; }
"""



# --------------------------------- Générateur principal --------------------------------------------

@anvil.server.callable
def enquete_suivi_tuteurs_pdf_gen(stage_row, role="T", type="suivi"):
    """
    Produit un PDF 'Résultat Formulaires de suivi de stages' pour un stage donné.
    - stage_row: ligne du stage (contient p.ex. 'numero', 'code', 'date_debut')
    - role: 'S' (Stagiaire) ou 'T' (Tuteur), par défaut 'S'
    """
    # Métadonnées stage
    stage_num = str(stage_row.get('numero') if hasattr(stage_row, 'get') else stage_row['numero'])
    stage_code = (stage_row.get('code') or {}).get('code') if hasattr(stage_row, 'get') else stage_row['code']['code']
    date_txt = stage_row.get('date_debut').strftime("%Y-%m-%d")  # ton PDF montre AAAA-MM-JJ
    titre_haut = "Formulaires de suivi des Tuteurs"
    sous_titre = f"Stage {stage_code} ({stage_num}) du {date_txt}"

    # Récupération des formulaires de ce stage + rôle
    forms = app_tables.stage_suivi.search(stage_num_txt=stage_num, user_role=role)
    
    # Construire les blocs stagiaires
    people_blocks = []
    for formulaire in forms:
        # Lecture nom/prénom du tuteur
        tuteur_user_row = app_tables.users.get(email=formulaire['user_email'])
        nom = tuteur_user_row['nom']
        prenom = tuteur_user_row['prenom']

        # Récupérer les réponses propres à ce formulaire
        rep_ouv = formulaire.get('rep_dico_rep_ouv') or {}
        rep_ferm = formulaire.get('rep_dico_rep_ferm') or {}

        open_html = _render_open_blocks(rep_ouv)
        ratings_html = _render_ratings_table(rep_ferm)

        people_blocks.append(f"""
        <section class="person-card">
            <div class="person-head">
              <div class="person-name">{_esc(prenom)} {_esc(nom)}</div>
            </div>
            {open_html}
            {ratings_html}
        </section>
        """)

    now = datetime.now(TZ_PARIS) if TZ_PARIS else datetime.now()
    gen_txt = now.strftime("%d/%m/%Y %H:%M")
    # -----------------------------------------------------------------------
    # HTML complet
    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{_esc(titre_haut)}</title>
    <style>{_css()}</style>
  </head>
  <body>
    <!-- En-têtes répétés -->
    <div class="page-header">
      <div class="h1">{_esc(titre_haut)}</div>
      <div class="h2">{_esc(sous_titre)}</div>
    </div>
    <div class="page-header-right">{_esc(gen_txt)}</div>

    {''.join(people_blocks) if people_blocks else '<p>Aucune réponse trouvée.</p>'}
  </body>
</html>
"""
    #------------------------------------------------------------------------------
    css = _css()   # Récupération du CSS
    return anvil.server.call("render_pdf", html_doc, css)  # dans module weasyprint 
