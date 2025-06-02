from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import French_zone # calcul tps traitement

#from ..._Constant_parameters_public_ok import nb_fiche_stagiaire_pdf   # pour param nb de fiches à imprimer 
from anvil_extras.PageBreak import PageBreak
global cpt      # ATTENTION, si j'utilise self.cpt, le décrément ne s'effectue pas
cpt = 0

# Repeating panel appelée par Visu_liste_1_stage, affichage des fiches stagiaires
class ItemTemplate2(ItemTemplate2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.      
        # lecture de la table des variables globales, paramètre 'nb_fiche_stagiaire_pdf'
        row_glob_var = app_tables.global_variables.get(name="nb_fiche_stagiaire_pdf")
        if row_glob_var:
            self.nb_fiche_stagiaire_pdf = int(row_glob_var['value']) 
            print("self.nb_fiche_stagiaire_pdf: ", self.nb_fiche_stagiaire_pdf)
        else:
            print("lecture de la table des variables globales, paramètre 'nb_fiche_stagiaire_pdf' a échoué")
            return
            
        # initialisation du nb de stagiares
        nb_stagiaires=self.item['stage']['nb_stagiaires_deb']
        print("nb_stagiaires: ", nb_stagiaires)
        
        # initialisation du cpt de fiche par page
        global cpt
        if nb_stagiaires <= self.nb_fiche_stagiaire_pdf:
            # si le nb de stgiaires est inf aux param globaux (nb_fiche_stagiaire_pdf) 
            #   j'élève le cpt pour qu'il n'y ai pas de saut de page
            cpt=5
        else:    
            # Ex: si nb stagiaires = 5, j'initialise le compteur d'image de la page à 5. Qd fonction image_1_show s'exécute, self.cpt sera décrémenté de 1
            #  donc, au bout de 5 stagiaires affichés le cpt = 0, donc saut de page  (voir fonction image_1_show)
            # si nb de stgiares multiple de 5 (10,15,20,25,30 ...)
            if self.nb_fiche_stagiaire_pdf==1:
                    cpt = 1
            if self.nb_fiche_stagiaire_pdf==5:
                if  nb_stagiaires in (10,15,20,25,30,35,40) :  # ok
                    cpt = 1
                if  nb_stagiaires in (9,14,19,24,29,34,39) :  # ok
                    cpt = 5
                if  nb_stagiaires in (8,13,18,23,28,33,38) :   # ok
                    cpt = 4
                if  nb_stagiaires in (7,12,17,22,27,32,37) :  # ok
                    cpt = 3
                if  nb_stagiaires in (6,11,16,21,26,31,36) : # ok
                    cpt = 2
            if self.nb_fiche_stagiaire_pdf==4:   
                if  nb_stagiaires in (8,12,16,20,24,28,32,36,40) :  # ok
                    cpt = 1
                if  nb_stagiaires in (7,11,15,19,23,27,31,35,39) :  # ok
                    cpt = 4
                if  nb_stagiaires in (6,10,14,18,22,26,30,34,38) :   # ok
                    cpt = 3
                if  nb_stagiaires in (5,9,13,17,21,25,29,33,37) :   # ok
                    cpt = 2
            if self.nb_fiche_stagiaire_pdf==3:
                if  nb_stagiaires in (6,9,12,15,18,21,24,27,30,33,36,39) :  # ok
                    cpt = 1
                if  nb_stagiaires in (5,8,11,14,17,20,23,26,29,32,35,38) :  # ok
                    cpt = 3
                if  nb_stagiaires in (4,7,10,13,16,19,22,25,28,31,34,37) :   # ok
                    cpt = 2
            if self.nb_fiche_stagiaire_pdf==2:
                if  nb_stagiaires in (4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40) :  # ok
                    cpt = 1
                if  nb_stagiaires in (3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39) :  # ok
                    cpt = 2
               
                    
        #lecture fichier users à partir du mail
        mel=self.item["user_email"]['email']
        stagiaire = app_tables.users.get(   q.fetch_only("photo", 'date_naissance', 'nom', 'prenom', 'email', 'tel', 'ville_naissance','code_postal_naissance','pays_naissance','adresse_rue','adresse_code_postal','adresse_ville'),
                                            email=mel)    
        if stagiaire :
            start = French_zone.french_zone_time()  # pour calcul du tps de traitement (environ 25 se)
            #Photo
            self.image_1.source = stagiaire['photo']
            end = French_zone.french_zone_time()
            print("Temps de traitement image: ", end-start)
            
            # self.text_box_5.text
            fi = self.item["financement"]["code_fi"]
            finance = app_tables.mode_financement.get(code_fi=fi)
            #self.text_box_5.text = finance['intitule_fi']

            self.rich_text_1.border="0px solid blue"
            self.rich_text_1.font_size=14
            self.rich_text_1.bold=False
            self.rich_text_1.italic=False
            self.rich_text_1.align="center"
            #self.rich_text_1.font="Noto"
            try: # si pas date de naissance, (user type T, F, A, )
                date_naiss_format = stagiaire['date_naissance'].strftime("%d/%m/%Y")
                self.rich_text_1.content=f" **{stagiaire['nom']} {stagiaire['prenom']}** ({finance['code_fi']}) \n{stagiaire['email']} \n {stagiaire['tel']} "
                self.rich_text_2.content=f" Né le {date_naiss_format} à {stagiaire['ville_naissance']} ({stagiaire['code_postal_naissance']} {stagiaire['pays_naissance']}) \n {stagiaire['adresse_rue']}, {stagiaire['adresse_code_postal']} {stagiaire['adresse_ville']} "
                
            except:
                self.rich_text_1.content=f" **{stagiaire['nom']} {stagiaire['prenom']}**  \n{stagiaire['email']} \n {stagiaire['tel']} "
                self.rich_text_2.content= ""


    def image_1_show(self, **event_args):
        #This method is called when the Image is shown on the screen
        global cpt        # nb d'images imprimées
        print("cpt: ", cpt)
        cpt -= 1       
        if cpt == 0:          # ts les 1 ou 5 stagiaires, selon param global nb_fiche_stagiaire_pdf
           self.add_component(PageBreak())      # si en création de pdf, je saute une page ts les n stagiares 
           print("break") 
           cpt = self.nb_fiche_stagiaire_pdf    # réinitialisation du nb de fiche par page avec le param global
