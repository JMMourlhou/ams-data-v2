import anvil.server


def open_whatsapp(telephone, text_msg):

    telephone = str(telephone).strip()
    telephone = telephone.replace(" ", "").replace(".", "").replace("-", "")

    if telephone.startswith("0"):
        telephone = "33" + telephone[1:]

    elif telephone.startswith("+"):
        telephone = telephone[1:]

    text_msg_encode = anvil.js.window.encodeURIComponent(text_msg)

    url_whatsapp = f"https://wa.me/{telephone}?text={text_msg_encode}"

    anvil.js.window.open(url_whatsapp, "_blank")