# Server Module
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import os
import tempfile
from pdf2image import convert_from_path
from typing import List
import io
import pypdf   # pour le module du calcul de nb de pages

@anvil.server.callable
def get_pdf_page_count(pdf_file):
    """
    Lit un fichier PDF et retourne le nombre de pages.
    L'entrée 'pdf_file' est un objet media Anvil.
    """
    try:
        # pypdf.PdfReader a besoin d'un objet de type fichier
        # 1. Récupère le contenu du fichier sous forme d'octets
        file_bytes = pdf_file.get_bytes()

        # 2. Crée un objet BytesIO en mémoire
        pdf_stream = io.BytesIO(file_bytes)

        # 3. Passe l'objet BytesIO "seekable" à pypdf
        pdf_reader = pypdf.PdfReader(pdf_stream)
        return len(pdf_reader.pages)
    except pypdf.errors.PdfReadError:
        # Gère les erreurs si le fichier n'est pas un PDF valide
        return "Le fichier n'est pas un PDF valide."

#_______________________________________________________________________________________
@anvil.server.background_task
def process_pdf_background(pdf_file, stage_row, email_row):
    try:
        images = get_images_from_pdf_file(pdf_file)                #fonction ds ce même module qui extrait la premier page du pdf

        # Enregistre la première image dans la base de données stagiaires_inscrits temporairement
        if images:
            first_image = images[0]
            row_stagiaire_inscrit = app_tables.stagiaires_inscrits.get(
                stage=stage_row,
                user_email=email_row
            )
            if row_stagiaire_inscrit:
                print(f"Ecriture du PDF en JPG de {row_stagiaire_inscrit}")
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
            return [anvil.media.from_file(im_path)]      # retour à la fonction process_pdf_background dans ce module
        else:
            return []

# Callable depuis le client pour lancer la tâche de fond
@anvil.server.callable
def process_pdf(pdf_file, stage_row, email_row):
    task = anvil.server.launch_background_task("process_pdf_background", pdf_file, stage_row, email_row)
    return task
