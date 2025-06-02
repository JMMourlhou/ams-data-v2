from ._anvil_designer import Visu_liste_1_stageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media                               # pour le pdf standard

global pdf_mode
pdf_mode=False

# Affichage et génération du pdf des fiches stagiaires du stage
# appelera V.ItemTemplate2

class Visu_liste_1_stage(Visu_liste_1_stageTemplate):
    def __init__(self, stage_num, intitule, pdf_mode=False, **properties):    #si pdf_mode=True ouverture pour pdf
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.
        self.f = get_open_form()
        self.num_stage = stage_num
        self.intitule = intitule
        self.pdf_mode = pdf_mode
        if self.pdf_mode is True:                 # mode pdf renderer
            self.column_panel_boutons.visible = False
            self.button_annuler.visible = False
            self.button_trombi.visible = False
            
        stagiaires_liste =  app_tables.stagiaires_inscrits.search(  q.fetch_only("name", "prenom", "stage", 
                                                                                user_email=q.fetch_only()),
                                                                    tables.order_by("name", ascending=True),
                                                                    numero=int(self.num_stage)
                                                                )
        self.repeating_panel_1.items = stagiaires_liste
        self.stage_row = stagiaires_liste[0]['stage']
        # nom de la forme       
        cod = self.stage_row["code_txt"]
        date = str(self.stage_row["date_debut"].strftime("%d/%m/%Y"))
        self.label_titre.text = "Fiches stagiaires " + cod + " du " + date + "   (num " + str(self.num_stage) +")"

    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form(self.f)

    def button_trombi_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Visu_trombi import Visu_trombi
        open_form('Visu_trombi',self.num_stage, self.intitule)

    def button_fiche_pdf_click(self, **event_args):
        """This method is called when the button is clicked"""
        stage_row = app_tables.stages.get(numero=int(self.num_stage))
        pdf = stage_row["list_media"]
        if pdf:
            anvil.media.download(pdf)
            alert("Fiches téléchargées")
        else:
            alert("Pdf des fiches non trouvé")


