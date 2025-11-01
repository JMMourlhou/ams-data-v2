from ._anvil_designer import ItemTemplate10_jmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Plot import Plot

class ItemTemplate10(ItemTemplate10_jmTemplate):   # Bt QCM results
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.button_qcm_descro.text = self.item['qcm_number']['destination']
        self.button_qcm_descro.tag.num_qcm = self.item['qcm_number']
        self.stagiaire = self.item['user_qcm']  #pour l'affichage du plot du stgiaire si bt qcm clicked
        self.num_qcm = self.item['qcm_number']['qcm_nb'] #pour l'affichage du plot du stgiaire si bt qcm clicked
        
        self.button_qcm_time.text = "le " + str(self.item['time'].strftime("%d/%m/%Y")) + " à " + str(self.item['time'].strftime("%Hh%M")) 
        if self.item['success'] is True:
            self.button_qcm_result.background = "green"
            self.button_qcm_result.foreground = "white"
            self.button_qcm_time.background = "green"
            self.button_qcm_time.foreground = "white"
        else:
            self.button_qcm_result.background = "red"
            self.button_qcm_time.background = "red"
        self.button_qcm_time.tag.num_qcm = self.item['qcm_number']
        
        self.button_qcm_result.text = str(self.item['p100_sur_nb_rep']) + " %"
        self.button_qcm_result.tag.num_qcm = self.item['qcm_number']

    def button_qcm_descro_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.column_panel_plot.visible is False:
            self.button_qcm_descro.foreground = "red"
            # Affichage du plot
            self.column_panel_plot.clear()
            self.column_panel_plot.visible = True
            self.button_download.visible = True
            #print("self.qcm_nb: ", self.qcm_nb)
            nb = self.button_qcm_descro.tag.num_qcm
            # plotly 
            affiche_next_qcm = False
            affiche_legende = False   # afficher la légende
            self.column_panel_plot.add_component(Plot(self.stagiaire, self.num_qcm, affiche_next_qcm, affiche_legende))   # nb:num de qcm   True:afficher la légende
        else:
            self.column_panel_plot.visible = False
            self.button_qcm_descro.foreground = "blue"
            self.button_download.visible = False

    def button_qcm_result_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_qcm_descro_click()

    def button_qcm_time_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_qcm_descro_click()

    def button_download_click(self, **event_args):
        """This method is called when the button is clicked"""
        affiche_next_qcm = False
        affiche_legende = False   # afficher la légende
        pdf = anvil.server.call("create_qcm_plot_pdf",self.stagiaire, self.num_qcm, affiche_next_qcm, affiche_legende)
        if pdf:
            anvil.media.download(pdf)
            alert("PDF 'Résultat QCM' téléchargé !")
        else:
            alert("Pdf du QCM non généré")
