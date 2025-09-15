from weasyprint import HTML, CSS
import anvil.server
import anvil.media

@anvil.server.callable
def render_pdf(html: str, css: str):
    """
    Permet de générer n'importe quel PDF, à partie d'un HTML et CSS construit auparavant 
    
    Reçoit un HTML complet (avec balises <html> ... ),
    Reçoit un CSS complet
    génère un PDF avec WeasyPrint et renvoie un BlobMedia.
    """
    pdf_bytes = HTML(string=html, base_url=".").write_pdf(
        stylesheets=[CSS(string=css)]
    )
    return anvil.BlobMedia("application/pdf", pdf_bytes)