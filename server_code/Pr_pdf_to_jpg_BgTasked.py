import anvil.email
# Transform a pdf file loaded into 1 or several pictures
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
filename=""

@anvil.server.background_task
def pdf_into_jpg_bg(pdf_file, new_file_name, stage_row, email_row) -> List:  
    # file est un pdf qui vient d'être choisi par le user
    # new_file_name est sans extension
    # stage_row et email row: pour sauver l'image jpg générée en table du stagiaire inscrit, col  "temp_pr_pdf_img"
    global filename
    filename = new_file_name       
    media = pdf_file
    #return get_pdf_file_images(media=pdf_file)             # à sauver
    # sauvegarde de la liste ds le row temp du stgiaire inscrit
    #liste = str(list(get_pdf_file_images(media))[0])   # 1ere image
    liste = get_pdf_file_images(media)[0]  # 1ere image
    print("type", type(liste))
    row_stagiaire_inscrit = app_tables.stagiaires_inscrits.get(q.fetch_only("temp_pr_pdf_img"),
                                                                    stage= stage_row,
                                                                    user_email=email_row
                                                                )
    if row_stagiaire_inscrit:
        row_stagiaire_inscrit.update(temp_pr_pdf_img = liste)

def get_pdf_file_images_from_url(pdf_file_url: str) -> List:
    with tempfile.TemporaryDirectory() as tmpdirname:
        pdf_file_path = os.path.join(tmpdirname, 'tmp.pdf')
        _download_file(pdf_file_url, pdf_file_path)
        return get_images_from_pdf_file(pdf_file_path, tmpdirname)             


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
    print("nb img ;",len(images))
    return [anvil.media.from_file(fpath) for fpath in images]          
             

def pdf_to_jpg(source_file_path: str, target_folder_path: str) -> List[str]:    # new file name rentré à la place de page 
    global filename                                          # global file name
    images = convert_from_path(source_file_path)
    im_paths = []
    for i in range(len(images)):
        # Save pages as images in the pdf
        #im_name = 'page' + str(i) + '.jpg'
                                      
        im_name = filename + '.jpg'                                    # <--  ajout extension
        print("pr_pdf_to_jpg_BgTasked, img full name; ",im_name)                         
        
        path = os.path.join(target_folder_path, im_name)     
        im_paths.append(path)
        images[i].save(path, 'JPEG')
        if i == 0:                                                     # 1ere image traitée, je sors 
            break
    return im_paths
    
# -----------------------------------------------------------------------------------------
# A FAIRE APPELER from client side
@anvil.server.callable
def pdf_into_jpg_bgtasked(pdf_file, new_file_name,stage_row, email_row):
    print("bg task timer1,nom, new_name: ",pdf_file.name, new_file_name, stage_row, email_row)
    task = anvil.server.launch_background_task("pdf_into_jpg_bg",pdf_file, new_file_name,stage_row, email_row)
    return task