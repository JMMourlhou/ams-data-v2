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
def make_trombi_pdf_via_uplink(rows, num_stage: int, intitule: str,
                               cols: int = 5, lines_per_page: int = 2,
                               title_enabled: bool = True):
    """
    Construit un HTML paginé par blocs 'cols * lines_per_page' cartes.
    Appelle l'Uplink (Pi5) 'render_trombi_pdf' et renvoie un BlobMedia PDF.
    """
    # Récup du stage info pour le titre
    stage_row = app_tables.stages.get(numero=int(num_stage))
    if not stage_row:
        raise ValueError(f"Stage {num_stage} introuvable")
        
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
        img_tag = f'<img class="trombi" src="{data_url}"/>' if data_url else ""

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

    blocks = []
    for i, card in enumerate(cards_html, start=1):
        # ouvre une grille au début de page
        if (i - 1) % per_page == 0:
            blocks.append(f'<div class="grid" style="grid-template-columns: repeat({per_row}, 1fr);">')

        blocks.append(card)

        # fin de page ?
        if (i % per_page == 0) and (i != len(cards_html)):
            blocks.append('</div>')  # close grid
            blocks.append('<div class="page-break"></div>')
        elif i == len(cards_html):
            blocks.append('</div>')  # close last grid

    grid_pages_html = "\n".join(blocks)

    stage_code = stage_row["code"]['code']
    date_txt = stage_row["date_debut"].strftime("%d/%m/%Y")
    title = _escape(f"Trombi stagiaires {stage_code} du {date_txt} (Stage {num_stage})")

    # HTML final (la CSS principale est dans ton Uplink, via CSS_BASE)
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
      .doc-title {{ font-size: 18px; font-weight: bold; margin: 0 0 8px 0; }}
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
    return anvil.server.call("render_trombi_pdf", html, filename)

