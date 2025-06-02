import anvil.email
# Display a pdf file loaded into 1 or several pictures (appelé par mailing Mail_suject_attach_txt, bouton attachements, qd user choisit d'envoyer un pdf)
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media
import anvil.server
import os
import tempfile
from pdf2image import convert_from_path
import requests
from typing import List
from io import BytesIO
from shutil import copyfile
global filename 
filename="temp"

# Ce module n'est pas utilisé
@anvil.server.callable
def display_pdf(file) -> List:   # file est un pdf qui vient d'être choisi par le user
    global filename
    filename = "temp"     # ce fichier pdf sera affiché (son nom n'a pas d'importance)

    media = file                      # Lecture du doc pdf ds table
    print(media.name)
    return get_pdf_file_images(media=media)  


def get_pdf_file_images(media: anvil.media) -> List:
    with tempfile.TemporaryDirectory() as tmpdirname:
        pdf_file_path = os.path.join(tmpdirname, media.name)
        _write_file(pdf_file_path, media)
        return get_images_from_pdf_file(pdf_file_path, tmpdirname)             

def _write_file(file_name, media):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "wb") as f:                        # with permet de fermer auto le fichier binaire à la fin
        if type(media) == BytesIO:
            _write_bytes_io(file_name, media)
        else:
            f.write(media.get_bytes())


def _write_bytes_io(file_name: str, bytes_io_file: BytesIO):
    bytes_io_file.seek(0)
    with open(file_name, 'wb') as f:
        shutil.copyfileobj(bytes_io_file, f)


def _download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download the file.")


def get_images_from_pdf_file(pdf_file_path: str, target_folder: str) -> List:
    images = pdf_to_jpg(source_file_path=pdf_file_path, target_folder_path=target_folder)       
    return [anvil.media.from_file(fpath) for fpath in images]


def pdf_to_jpg(source_file_path: str, target_folder_path: str) -> List[str]:    # new file name rentré à la place de page 
    global filename                                          # global file name
    
    images = convert_from_path(source_file_path)
    im_paths = []
    for i in range(len(images)):
        # Save pages as images in the pdf
        #im_name = 'page' + str(i) + '.jpg'
        im_name = filename + str(i) + '.jpg'                  # <--  Ici
        print("pdfinto img:",im_name)                         # ok
        
        path = os.path.join(target_folder_path, im_name)     
        im_paths.append(path)
        images[i].save(path, 'JPEG')
    return im_paths
  