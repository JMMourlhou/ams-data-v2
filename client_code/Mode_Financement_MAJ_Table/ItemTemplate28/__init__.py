from ._anvil_designer import ItemTemplate28Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate28(ItemTemplate28Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.init_components(**properties)

        self.text_box_2.text = self.item['code_fi']
        self.text_box_1.text = self.item['intitule_fi']
        self.sov_old_code = self.item['code_fi']
        self.sov_old_intitule = self.item['intitule_fi']

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        r=alert("Voulez-vous vraiment effacer ce mode de financement ?",dismissible=False,buttons=[("oui",True),("non",False)])
        if r :   # oui
            result,nb,liste = anvil.server.call("del_mode_fi", self.item, self.item['code_fi'])
            if result is not True:
                detail=[]
                for stagiaire in liste:
                    detail.append((stagiaire['numero'],stagiaire['name'],stagiaire['prenom']))
                alert(f"Effacement non effectué, ce mode de financement est utilisé par {nb} stagiaire(s) :\nStagiaires(s): {detail}")
                return
            alert("Effacement effectué !")
        open_form("Mode_Financement_MAJ_Table")

    def text_box_2_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def text_box_1_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.button_modif.visible = True

    def button_modif_click(self, **event_args):
        """This method is called when the button is clicked"""
        # vérif si ce code de financement existe déjà ?
        test = app_tables.mode_financement.search(code_fi=self.text_box_2.text)
        if len(test)==1 and self.text_box_2.text != self.sov_old_code:
            alert("Ce code existe déjà !")
            self.text_box_2.focus()
            return
        r=alert("Voulez-vous vraiment modifier ce Mode de Financement ?",buttons=[("oui",True),("non",False)])
        if r :   # oui
            # modif du mode de fi 
            result = anvil.server.call("modif_mode_fi", self.item, self.text_box_2.text, self.text_box_1.text, self.sov_old_intitule)
            if result is not True:
                alert("ERREUR, Modification non effectuée !")
                return
            alert("Modification effectuée !")
            
        else:   # non
            self.text_box_1.text = self.sov_old_intitule
            self.text_box_2.text = self.sov_old_code
        self.button_modif.visible = False