from ._anvil_designer import Stage_satisf_rep_ouvertesTemplate
from anvil import *
import anvil.server
from anvil_extras.PageBreak import PageBreak


# AFFICHAGE DES RESULTATS d pour 1 question ouverte du formulaire de satisfaction
# APPELE PAR LA FORM 'STAGE_SATISF_STATISTICS' par add component:
#   (  self.column_panel_content.add_component(Stage_satisf_histograms(qt,r0,r1,r2,r3,r4,r5)) )


class Stage_satisf_rep_ouvertes(Stage_satisf_rep_ouvertesTemplate):
    def __init__(self, qt, list_rep, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label_question.text = qt
        for rep in list_rep:
            self.tb = RichText(
                             content=rep,
                             align = "left",
                             spacing_above = "none",
                             background="",
                             foreground="black",
                             #bold=False,
                             font_size = 12,
                             #enabled = False
                             spacing_below = "none"
                            )
            
            self.column_panel_reponses.add_component(self.tb)  # add 1 des réponses)

          
    def form_show(self, **event_args):
        self.add_component(PageBreak())      # si en création de pdf, je saute une page ts les 25 images, NE FONCTIONNE PAS !!!