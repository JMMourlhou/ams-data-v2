import anvil.email
import anvil.tables as tables
import anvil.server
import pathlib
from PIL import Image
import io

# Change an img size to 800 x 600
# if img_future_name not empty: Change its name
# set it as jpg image

@anvil.server.callable
def resize_img(file, img_future_name=None):
    path = pathlib.Path(file.name)
    name = str(path.name)
    extension = str(path.suffix)  # path, file name, extension
    lg_totale = len(name)
    lg_ext = len(extension)
    suffixe = name[0:lg_totale-lg_ext]
    
    # Convert the 'file' Media object into a Pillow Image
    img = Image.open(io.BytesIO(file.get_bytes()))
    width, height = img.size
    # Resize the image to the required size according to landscape / or not
    if width >= height:   #landscape
        img = img.resize((800,600))
    else: 
        img = img.resize((600,800))
    
    img = img.convert("RGB")
    
    # Convert the Pillow Image into an Anvil Media object and return it
    bs = io.BytesIO()
    img.save(bs, format="JPEG")
    
    if img_future_name is None:
        new_name = suffixe + ".jpg"
    else:
        new_name = img_future_name + ".jpg"
        
    return anvil.BlobMedia("image/jpeg", bs.getvalue(), name=new_name)