from ._anvil_designer import ItemTemplate16Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate16(ItemTemplate16Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.f = get_open_form()   # récupération de la forme mère pour accéder aux fonctions et composents
        print("form mère atteingnable (en modif): ", self.f) 
        
        #self.image_doc.source = self.item[0]        # 1er élément de l'item, le media file choisit pour téléchargement (si pdf, le transfomer en jpg)
        self.label_address_doc.text = self.item[1]  # 2eme élément de l'item, le nom du fichier en txt
        
        # Type de fichier en attachement ?
        path_parent, file_name, file_extension = anvil.server.call('path_info', str(self.item[0].name))
        file_extension = file_extension[0:4].lower() # 4 1ers caract en minuscule   ex;    .XLSX > .xls
        print(file_extension)
        """
        if file_extension == ".pdf":
            liste_images = anvil.server.call('display_pdf', self.item[0]) 
        
            #extraction 1ere image de la liste (il peut y avoir plusieurs pages)
            print("nb d'images jpg crées par pdf_into_jpg:", len(liste_images))
            file = liste_images[0]
            self.image_doc.source =  file
        """
        if file_extension == ".jpg":
            self.image_doc.source = self.item[0]        # 1er élément de l'item, le media file choisit pour téléchargement (si pdf, le transfomer en jpg)
        if file_extension == ".png":
            self.image_doc.source = self.item[0]
        if file_extension == ".jpe":
            self.image_doc.source = self.item[0]  # pas d'affichage
        if file_extension == ".hei":
            self.image_doc.source = self.item[0] # pas d'affichage
        if file_extension == ".gif":
            self.image_doc.source = self.item[0] 
        if file_extension == ".bmp":
            self.image_doc.source = self.item[0] 
            
        if file_extension == ".xls":
            self.image_doc.source = self.f.icone_xls
        if file_extension == ".doc":
            self.image_doc.source = self.f.icone_doc
        if file_extension == ".pps":
            self.image_doc.source = self.f.icone_ppt
        if file_extension == ".pdf":
            self.image_doc.source = self.f.icone_pdf  

    
    def button_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.f = get_open_form()   # récupération de la forme mère pour accéder aux fonctions et composents
        print("form mère atteingnable (en modif): ", self.f) 
        
        self.f.list_attach = [] # réinitialisation de la liste pour le repeating panel
        del  self.f.dico_attachements[self.item[0]]
        
        for clef, valeur in self.f.dico_attachements.items():
                self.f.list_attach.append((clef,valeur))  # transformation dict en liste pour le repeating panel
        
        self.f.repeating_panel_2.items = self.f.list_attach
