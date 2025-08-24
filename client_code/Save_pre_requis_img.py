import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media
from .import Pre_R_doc_name        # Pour générer un nouveau nom au document chargé
from .import French_zone # pour calcul tps traitement

def save_file(item_row, file):
    # pour calcul du temps de traitement
    start = French_zone.french_zone_time()  # pour calcul du tps de traitement
    # Appel du script d'écriture chargé for ever sur Pi5 
    message = anvil.server.call("pre_requis", item_row, file)
    end = French_zone.french_zone_time()
    print(f"Temps de traitement image: {end-start}, result: {message}")