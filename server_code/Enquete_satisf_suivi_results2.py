from anvil.tables import app_tables
import anvil.server
import html, re, unicodedata
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_PARIS = ZoneInfo("Europe/Paris")
except Exception:
    TZ_PARIS = None

# ------------------ Helpers ------------------

def _esc(s):
    if s is None:
        return ""
    return html.escape(str(s))

def _clean_text(s):
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", s)
    return s

def _user_from_email(email_or_obj):
    """Retourne (prenom, nom, tel, email_str) depuis la table users."""
    email_str, tel = None, None
    if isinstance(email_or_obj, dict):
        email_str = email_or_obj.get("email")
        tel = email_or_obj.get("tel")
    else:
        email_str = email_or_obj
    u = app_tables.users.get(email=email_str) if email_str else None
    prenom = (u and u.get("prenom")) or ""
    nom = (u and (u.get("nom") or u.get("name"))) or ""
    tel = (u and (u.get("tel") or (u.get("user_email") or {}).get("tel"))) or tel
    return prenom, nom, tel or "", email_str or ""

def _render_open_blocks(rep_ouv: dict) -> str:
    """Affiche les questions ouvertes en style stagiaires/tuteurs (bandeau bleu + réponses)."""
    blocks = []
    for k, vals in (rep_ouv or {}).items():
        if not vals:
            continue
        if isinstance(vals, (list, tuple)):
            qlabel = vals[0]
            answers = vals[1:]
        else:
            qlabel = str(k)
            answers = [str(vals)]
        qlabel = _clean_text(qlabel)
        lis = "".join(f"<li>{_esc(_clean_text(v))}</li>" for v in answers if v)
        answer_html = f"<ul class='qa-list'>{lis}</ul>" if lis else "<div class='qa-empty'>—</div>"
        blocks.append(f"""
          <section class="qa-block">
            <div class="qa-title">
              <span class="qlabel">{_esc(qlabel)}</span>
            </div>
            {answer_html}
          </section>
        """)
    return "".join(blocks)

def _render_ratings_table(rep_ferm: dict) -> str:
    """
    Affiche les questions fermées dans un tableau coloré,
    avec barre visuelle et coloration selon la note (0-5).
    """
    if not rep_ferm:
        return ""

    rows = []
    for k, v in rep_ferm.items():
        qnum = None
        label = ""
        value = v

        # Forme A : clé = numéro, valeur = [label, note]
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            qnum = str(k)
            label = str(v[0])
            value = v[1]
        else:
            # Forme B : clé = libellé, valeur directe
            label = str(k)

        # Normalisation valeur
        value_txt = str(value)
        score = None
        try:
            score = int(str(value).strip())
            score = max(0, min(5, score))  # bornage entre 0 et 5
        except Exception:
            score = None

        # Barre visuelle
        bar = ""
        if score is not None:
            bar = f"<div class='bar'><div class='bar-fill' style='width:{score*20}%'></div></div>"

        # Ligne du tableau avec classe score-X
        tr_class = f"score-{score}" if score is not None else ""
        rows.append(f"""
          <tr class="{tr_class}">
            <td class="qnum">{_esc(qnum) if qnum else ""}</td>
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
  @top-right     { content: element(doc-meta); }
}

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
  break-inside: avoid;
  page-break-inside: avoid;
}
.person-card + .person-card {
  break-before: page;
  page-break-before: always;
}
.person-card:last-child { page-break-after: auto; }
.person-head { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:baseline; justify-content: center; margin-bottom:8px; }
.person-name { font-weight:700; color:#B3261E; font-size:12.5pt; }
.person-tel  { font-size:9pt; color:#B3261E; }

/* Questions ouvertes */
.qa-block { margin: 8px 0; break-inside: avoid; }
.qa-title {
  display: grid;
  grid-template-columns: 1fr;
  align-items: center;
  font-weight: 700; color: #222;
  background: #f3f6ff;
  border-left: 3px solid #0047ab;
  padding: 6px 8px; border-radius: 4px;
  font-size: 10.5pt;
  width: 100%;
  box-sizing: border-box;
}
.qa-title .qlabel { color: #0047ab; font-weight: 700; }
.qa-list { margin: 6px 0 0 18px; }
.qa-empty { margin: 6px 0 0 6px; color:#777; }

/* Questions fermées */
.rating-table { width:100%; border-collapse:collapse; margin-top:8px; table-layout: fixed; }
.rating-table td { border:1px solid #d7dbe6; padding:6px; vertical-align:middle; }
.rating-table td.rlabel { word-wrap:break-word; overflow-wrap:anywhere; }
.rating-table td.rval { text-align:center; }
"""

# ------------------ Générateur principal ------------------

@anvil.server.callable
def enquete_suivi_pdf_generetor(stage_row, role="S"):
    stage_num = str(stage_row['numero'])
    stage_code = stage_row['code']['code']
    date_txt = stage_row['date_debut'].strftime("%Y-%m-%d")
    titre_haut = "Formulaires de suivi" if role == "S" else "Formulaires de suivi des Tuteurs"
    sous_titre = f"Stage {stage_code} ({stage_num}) du {date_txt}"

    forms = app_tables.stage_suivi.search(stage_num_txt=stage_num, user_role=role)

    people_blocks = []
    for f in forms:
        mel = f.get('user_email')
        if isinstance(mel, dict):
            mel = mel.get('email')
        prenom, nom, tel, email_str = _user_from_email(mel)

        if role == "S":
            # Stagiaire = un seul bloc
            open_html = _render_open_blocks(f.get('rep_dico_rep_ouv') or {})
            ratings_html = _render_ratings_table(f.get('rep_dico_rep_ferm') or {})
            people_blocks.append(f"""
            <section class="person-card">
              <div class="person-head">
                <div class="person-name">{_esc(prenom)} {_esc(nom)}</div>
                <div class="person-tel">{_esc(tel)}</div>
              </div>
              {open_html}{ratings_html}
            </section>
            """)
        else:
            # Tuteur = peut contenir plusieurs stagiaires
            rep_ouv = f.get('rep_dico_rep_ouv') or {}
            rep_ferm = f.get('rep_dico_rep_ferm') or {}

            blocs, current = [], {"ouv": {}, "ferm": {}}
            for k, vals in rep_ouv.items():
                if str(k).startswith("3") and current["ouv"]:
                    blocs.append(current)
                    current = {"ouv": {}, "ferm": {}}
                current["ouv"][k] = vals
            current["ferm"].update(rep_ferm)
            if current["ouv"] or current["ferm"]:
                blocs.append(current)

            for i, bloc in enumerate(blocs, 1):
                open_html = _render_open_blocks(bloc.get("ouv", {}))
                ratings_html = _render_ratings_table(bloc.get("ferm", {}))
                people_blocks.append(f"""
                <section class="person-card">
                  <div class="person-head">
                    <div class="person-name">{_esc(prenom)} {_esc(nom)} — Stagiaire {i}</div>
                    <div class="person-tel">{_esc(tel)}</div>
                  </div>
                  {open_html}{ratings_html}
                </section>
                """)

    now = datetime.now(TZ_PARIS) if TZ_PARIS else datetime.now()
    gen_txt = now.strftime("%d/%m/%Y %H:%M")

    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>{_esc(titre_haut)}</title>
<style>{_css()}</style></head>
<body>
<div class="page-header">
  <div class="h1">{_esc(titre_haut)}</div>
  <div class="h2">{_esc(sous_titre)}</div>
</div>
<div class="page-header-right">{_esc(gen_txt)}</div>
{''.join(people_blocks) if people_blocks else '<p>Aucune réponse trouvée.</p>'}
</body></html>
"""
    return anvil.server.call("render_pdf", html_doc, _css())
