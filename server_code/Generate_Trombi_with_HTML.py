# ServerModule_TrombiPDF
import anvil.server
import base64
from anvil.tables import app_tables
import anvil.tables as tables

def _media_to_data_url(media_obj):
    """Convertit un Media (image) en data URL base64 pour WeasyPrint."""
    if not media_obj:
        return None
    bs = media_obj.get_bytes()
    mime = media_obj.content_type or "image/jpeg"
    b64 = base64.b64encode(bs).decode("ascii")
            
    return f"data:{mime};base64,{b64}"

def _escape(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

@anvil.server.callable
def make_trombi_pdf_via_uplink(stage_row, rows, num_stage: int,                 # Stage_row et num_stage None si multi stages de même type (vient de Recherche)
                               cols: int = 5, lines_per_page: int = 2,
                               title_enabled: bool = True, type_stage_si_multi: str = None):
    """
    Construit un HTML paginé par blocs 'cols * lines_per_page' cartes.
    Appelle l'Uplink (Pi5) 'render_trombi_pdf' et renvoie un BlobMedia PDF.
    """

    # Fabrique les cards (image + textes)
    cards_html = []
    for r in rows:
        mel = r["user_email"]['email']
        u = app_tables.users.get(email=mel)
        if not u:
            continue

        nom = u.get('nom') or ""
        prenom = u.get('prenom') or ""
        nomprenom = _escape(f"{nom} {prenom}".strip())

        tel = r["user_email"].get('tel') or "Tel ?"
        if isinstance(tel, str) and len(tel) == 10 and tel.isdigit():
            tel = f"{tel[0:2]}-{tel[2:4]}-{tel[4:6]}-{tel[6:8]}-{tel[8:10]}"
        tel = _escape(tel)
        mel_esc = _escape(mel)

        data_url = _media_to_data_url(u.get('photo'))
        img_tag = f'''
        <div class="img-box">
          <img class="trombi" src="{data_url}"/>
        </div>''' if data_url else ""

        card = f"""
        <div class="card">
          {img_tag}
          <div class="name">{nomprenom}</div>
          <div class="tel">{tel}</div>
          <div class="mail">{mel_esc}</div>
        </div>
        """
        cards_html.append(card)

    per_row = max(1, int(cols))
    per_page = per_row * max(1, int(lines_per_page))

    def _table_for_cards(cards, per_row):
        # Construit un tableau 5 colonnes, n lignes, en remplissant les trous si besoin
        rows_html = []
        for i in range(0, len(cards), per_row):
            row_cards = cards[i:i+per_row]
            tds = "\n".join(f"<td class='card'>{c}</td>" for c in row_cards)
            # Complète les cellules manquantes pour garder 5 colonnes
            if len(row_cards) < per_row:
                tds += "\n" + "\n".join("<td class='card'></td>" for _ in range(per_row - len(row_cards)))
            rows_html.append(f"<tr>\n{tds}\n</tr>")
        return f"<table class='trombi'>\n{''.join(rows_html)}\n</table>"

    pages = []
    for i in range(0, len(cards_html), per_page):
        page_cards = cards_html[i:i+per_page]
        pages.append(_table_for_cards(page_cards, per_row))

    # Insère un saut de page entre les tableaux (pas après le dernier)
    grid_pages_html = ("<div class='page-break'></div>").join(pages)

    if stage_row is not None:   # 1 seul stage
        stage_code = stage_row["code"]['code']
        date_txt = stage_row["date_debut"].strftime("%d/%m/%Y")
        title = _escape(f"Trombi stagiaires {stage_code} du {date_txt} (Stage {num_stage})")
    else: # Multi stages
        title = _escape(f"Trombi stagiaires, tous stages {type_stage_si_multi}")
        num_stage = _escape(f"Trombi_stages_{type_stage_si_multi}")
        
    # =========================================================================================================
    # Fabrique le CSS pour les TROMBIS, contenu dans la variable 'CSS' de type text
    css = """
@page {
  size: A4;
  margin: 10mm;                    /* ≈ 1 cm */  
}

@media print {
  .page-break { break-after: page; page-break-after: always; }
  td.card { break-inside: avoid; page-break-inside: avoid; }
}
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

/* Table compacte et stable */
table.trombi {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
table.trombi td.card {
  width: 20%;                      /* 5 colonnes */
  box-sizing: border-box;
  vertical-align: top;
  border: 1px solid #ddd;
  padding: 6px;
  text-align: center;
}

/* Image cadrée uniformément (hauteur identique) */
.img-box {
  width: 100%;
  height: 38mm;                    /* ajuste 34–42 mm si besoin */
  overflow: hidden;
}
.img-box > img.trombi {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;               /* pas de distorsion */
}

/* Textes */
.name { color: #0047ab; font-size: 10pt; margin-top: 4px; }
.tel  { color: #0047ab; font-size: 10pt; }

/* 3) Email plus petit et cassable sur plusieurs lignes */
.mail {
  color: #0047ab;
  font-size: 7pt;                  
  line-height: 1.2;
  overflow-wrap: anywhere;         /* coupe proprement les longues adresses */
  word-break: break-word;
}
"""

    
    # =========================================================================================================
    # HTML final (la CSS principale est dans mon Uplink "render_trombi_pdf" hors du docker amsdata sur PI5)
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
      /* Footer en une seule ligne, centré */
      @page {{
        @bottom-center {{
          content: "{title} — Page " counter(page) " / " counter(pages);
          font-size: 9pt;
          color: #0047ab;
        }}
      }}
      /* Titre en haut, même couleur, centré */
      .doc-title {{
        color: #0047ab;
        text-align: center;
        font-weight: 700;
        font-size: 14pt;
        margin: 0 0 8px 0;
        page-break-after: avoid;
      }}
    </style>
  </head>
  <body>
    {f'<div class="doc-title">{title}</div>' if title_enabled else ''}
    {grid_pages_html}
  </body>
</html>
"""
    
    filename = f"trombi_{num_stage}.pdf"
    # Appel Uplink → Pi5
    return anvil.server.call("render_pdf", html, css, filename)

