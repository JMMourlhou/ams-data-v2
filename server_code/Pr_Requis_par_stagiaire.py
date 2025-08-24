import anvil.email
#from anvil import *
import pathlib
import anvil.files
import anvil.tables.query as q
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server
#from PIL import Image
import io
import math
from PIL import Image

@anvil.server.callable
def path_info(file):
    path = pathlib.Path(file)
    return str(path.parent), str(path.name), str(path.suffix).lower()  # path, file name, extension



# ===============================================================================================================
# PRE-REQUIS STAGIAIRES (ADMIN  voir leurs docs prérequis)
#     Pour lecture fichier père users: self.item['user_email']
#     Pour lecture fichier père stages: self.item['stage']
@anvil.server.callable
def preparation_liste_pour_panels_pr(user_email, stage):
    liste_pr = app_tables.pre_requis_stagiaire.search(
                                                        tables.order_by("requis_txt", ascending=True),
                                                        q.fetch_only("item_requis", "thumb", "stagiaire_email"),
                                                        stagiaire_email = user_email,        # user_email row
                                                        stage_num = stage                    # stage      row
                                                        )
    
    #list(liste_pr).sort(key=lambda x: x["item_requis"]["code_pre_requis"])      # TRI par code pré requis
    return liste_pr



"""
**************************************************** ECRITURE DE L'IMAGE JPG ou autre format img EN BGT 
Appelé par Pre_R_pour_stagiaire/
*************************************************************************************************
"""
@anvil.server.background_task
def modify_pre_r_par_stagiaire(pr_requis_row, file, new_file_name, file_extension):
    if pr_requis_row:
        if file_extension == ".jpg" or file_extension == ".jpeg" or file_extension == ".bmp"or file_extension == ".gif" or file_extension == ".jif" or file_extension == ".png":
            print("serveur Preq: Ce fichier est une image de type ",file_extension)        
            new_file_name = new_file_name + ".jpg"   # Le fichier sera resized et au format jpg

            #-------------------------------------------------------------------------------- à Remplacer par 1 B.G. task / loop traitmt images
            # Img file, Convert the 'file' Media object into a Pillow Image
            img = Image.open(io.BytesIO(file.get_bytes()))
            width, height = img.size
            print('run_bg_task_save_jpg, size img', width, height)
            taille = width * height
            #print("taille :", taille)
            if taille > 800000:    # si sup à 1000 x 800 ou   800 x 1000
                # img de  haute qualité je calcul le ratio pour ramener à 1000 x 800
                if width >= height:   #landscape
                    ratio = width/1000
                else: 
                    ratio = height/1000

                width = math.floor(width / ratio)            # je ne prends pas les virgules        
                height = math.floor(height / ratio)
                    
            # Resize the image to the required size
            img = img.resize((width,height))

            width, height = img.size
            taille = width * height
            #print('new_size', width, height)
            
            # Convert the Pillow Image into an Anvil Media object and return it

            img = img.convert("RGB")
            img_thumb = img                  # Je sauve l'img pour créer la petite img thumbnail
            bs = io.BytesIO()
            img.save(bs, format="JPEG")
            file = anvil.BlobMedia("image/jpeg", bs.getvalue(), name=new_file_name)
            
            width = math.floor(width / 6.666)   # la taille de l'img étant de 1000 x 800 ou   800 x 150 je ramene à 150 px  
            height = math.floor(height / 6.666)   # 1000 / 150
            img_thumb = img_thumb.resize((width,height))
            bs = io.BytesIO()                                                       
            img_thumb.save(bs, format="JPEG")
            file_thumb = anvil.BlobMedia("image/jpeg", bs.getvalue(), name=new_file_name)
               
            # -------------------------------------------------------------------------------------            
            
            # SAUVEGARDE IMG ds doc1, j'efface pdf_doc1 sinon je risque de télécharger un ancien fichier, je sauve le thumb
            pr_requis_row.update(check=True,               
                                doc1 = file,
                                thumb = file_thumb,
                                size = taille
                                )
            #return file_thumb

        if file_extension == ".pdf":
            print("serveur Preq: Ce fichier est un pdf")

@anvil.server.callable
def run_bg_task_save_jpg(pr_requis_row, file, new_file_name, file_extension):
    task = anvil.server.launch_background_task('modify_pre_r_par_stagiaire',pr_requis_row, file, new_file_name, file_extension)
    return task

"""
**************************************************************** FIN DU PRECESSUS BGT
"""




# ===============================================================================================================
# PRE-REQUIS STAGIAIRES, Effacement d'un pré-requis OU destruction
@anvil.server.callable
def pr_stagiaire_del(user_email, stage, item_requis, mode="efface"):
    pr_requis_row = app_tables.pre_requis_stagiaire.get(stage_num = stage,          # stage row
                                                         stagiaire_email = user_email,       # user row
                                                         item_requis = item_requis      # item_requi row                                      
                                             ) 
    if pr_requis_row and mode=="efface":
        pr_requis_row.update(check=False,               
                                doc1 = None,
                                thumb = None,
                                size = None
                                )
        return True
    if pr_requis_row and mode=="destruction":
        pr_requis_row.delete()
        return True
    return False
    
# ===============================================================================================================
# PRE-REQUIS STAGIAIRES TEST TIMING
@anvil.server.callable
def test_timing(dict):
    content_type = dict["content_type"]
    new_file = anvil.BlobMedia("image/png", file.get_bytes(), name=new_file_name)
    try:
        # SAUVEGARDE IMG ds doc1,inchangée, renommée
        pr_requis_row.update(check=True,               
                            doc1 = new_file,
                            #thumb = thumb,
                            #size = taille
                            )
        return True
    except:
        return False
    