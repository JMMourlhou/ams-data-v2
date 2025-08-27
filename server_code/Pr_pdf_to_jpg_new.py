# Server Module
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import os
import tempfile
from pdf2image import convert_from_path
from typing import List

@anvil.server.background_task
def process_pdf_background(pdf_file, stage_row, email_row):
    try:
        images = get_images_from_pdf_file(pdf_file)

        # Enregistre la première image dans la base de données
        if images:
            first_image = images[0]
            row_stagiaire_inscrit = app_tables.stagiaires_inscrits.get(
                stage=stage_row,
                user_email=email_row
            )
            if row_stagiaire_inscrit:
                row_stagiaire_inscrit.update(temp_pr_pdf_img=first_image)
                print("Première image du PDF enregistrée avec succès.")
        else:
            print("Aucune image n'a pu être extraite du PDF.")

    except Exception as e:
        print(f"Une erreur est survenue lors du traitement du PDF : {e}")

def get_images_from_pdf_file(media: anvil.media) -> List:
    """
    Extrait les images d'un objet media PDF.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Écrit le fichier media dans un fichier temporaire
        pdf_file_path = os.path.join(tmpdirname, media.name)
        with open(pdf_file_path, "wb") as f:
            f.write(media.get_bytes())

        # Convertit le PDF en images JPEG
        images = convert_from_path(pdf_file_path)

        # Sauvegarde la première page en tant que fichier temporaire
        # Le nom du fichier est basé sur le nom du fichier d'origine.
        im_path = os.path.join(tmpdirname, f"{os.path.splitext(media.name)[0]}_page_1.jpg")

        # Sauvegarde seulement la première image
        if images:
            images[0].save(im_path, 'JPEG')
            print(f"Première page convertie en JPEG : {im_path}")
            return [anvil.media.from_file(im_path)]
        else:
            return []

# Callable depuis le client pour lancer la tâche de fond
@anvil.server.callable
def process_pdf(pdf_file, stage_row, email_row):
    task = anvil.server.launch_background_task("process_pdf_background", pdf_file, stage_row, email_row)
    return task
