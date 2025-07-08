from anvil.js.window import document

def Page_Break():
    """
    Insère un saut de page HTML (utilisé uniquement pour les impressions).
    """
    br = document.createElement("div")
    br.classList.add("page-break")
    document.body.appendChild(br)
