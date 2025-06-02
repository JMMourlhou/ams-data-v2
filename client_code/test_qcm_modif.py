
import anvil.server

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .QCM_visu_modif import QCM_visu_modif

def test_deux_lignes_qcm():
    #from .. import QCM_visu_modif
    # je vérifie qu'1 seule ligne est modifiée à la fois (tous la ligne a le m^me numero) 
    cpt = 0
    for fl_p in QCM_visu_modif.get_components():  #ds chaque flow panel
        for cpnt in fl_p.get_components():
            print(f"{cpnt.tag.nom}  num:{cpnt.tag.numero}")
            if cpnt.background == "red":
                cpt += 1
                alert(f"{cpnt.tag.nom}  cpt:{cpt}")
                
                if cpt == 2:
                    alert("Ne modifier qu'une seule ligne à la fois !")
                
                
                    # rendre invalide tous les boutons 
                    for f in self.get_components():
                        for cp in fget_components():
                            if cp.tag.nom == "button":
                                cp.enabled = False
                                cp.background = "theme:Tertiary"
                                cp.foregroundground = "theme:Error"  

                                return("changements faits")
