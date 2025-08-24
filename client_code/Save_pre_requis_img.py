import anvil
import anvil.server
import anvil.media
#from .import Pre_R_doc_name        # Pour générer un nouveau nom au document chargé
from .import French_zone # pour calcul tps traitement
from PIL import Image
import io, math


def save_file(item_row, file):
    # pour calcul du temps de traitement
    start = French_zone.french_zone_time()  # pour calcul du tps de traitement
    # ---------------------------------------------------------------------------------
    img = Image.open(io.BytesIO(file.get_bytes()))
    width, height = img.size
    print("Taille d'origine:", width, height)

    # --- Redimensionner image principale si trop grande
    max_dim = 1000
    if max(width, height) > max_dim:
        ratio = max(width, height) / max_dim
        width = math.floor(width / ratio)
        height = math.floor(height / ratio)
        img = img.resize((width, height), Image.LANCZOS)

    print("Nouvelle taille (principale):", width, height)

    # --- Convertir et sauver en JPEG compressé (image principale)
    img_main = img.convert("RGB")
    bs_main = io.BytesIO()
    img_main.save(bs_main, format="JPEG", quality=80, optimize=True)
    main_file = anvil.BlobMedia("image/jpeg", bs_main.getvalue(), name="media.jpg")

    # --- Créer la miniature (thumbnail)
    img_thumb = img.copy()
    thumb_max_dim = 200
    img_thumb.thumbnail((thumb_max_dim, thumb_max_dim), Image.LANCZOS) #img.resize() sans filtre peut produire une perte de netteté.
    bs_thumb = io.BytesIO()
    img_thumb.save(bs_thumb, format="JPEG", quality=70, optimize=True)
    thumb_file = anvil.BlobMedia("image/jpeg", bs_thumb.getvalue(), name="thumb.jpg")


    # ---------------------------------------------------------------------------------
    # Appel du script d'écriture chargé for ever sur Pi5 
    message = anvil.server.call("pre_requis", item_row, main_file, thumb_file)
    end = French_zone.french_zone_time()
    print(f"Temps de traitement image: {end-start}, result: {message}")