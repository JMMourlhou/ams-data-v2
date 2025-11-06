from ._anvil_designer import Item_formulaires_suivis_listeTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Item_formulaires_suivis_liste(Item_formulaires_suivis_listeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.f = get_open_form()  # form appelante
        # Any code you write here will run before the form opens.
        self.button_num_stage.text = f"Num {self.item['stage_num_txt']}"
        self.button_type_stage.text = f"Suivi de stage {self.item['stage_type_txt']}"
        self.button_date_heure.text = f"Saisi le {self.item['date_heure'][0:16]}"
        if self.item['user_role']=="T":
            #lecture du nom prénom du stagiaire du Tuteur
            try:
                auteur_row = app_tables.users.get(email=self.item['stagiaire_du_tuteur'])
                nom = auteur_row['nom']
                prenom = auteur_row['prenom']
                self.button_suivi_pour.text = f"pour {nom} {prenom}"
                self.button_suivi_pour.visible = True
            except:
                pass # colonne vide
            

    def button_type_stage_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.f.repeating_panel_formul_suivi_questions_ouvertes.visible is False:
            # génération de la liste à afficher
            # QUESIONS OUVERTES Formulaires de suivi
            liste_questions_ouv=[]
            # dico questions ouvertes
            dico_rep_ouv = self.item["rep_dico_rep_ouv"]  # dico questions ouvertes du formulaire
            # Boucle sur le dictionaire ouvert du formulaire
            for cle, val in dico_rep_ouv.items():
                num_question = cle
                question = val[0]
                reponse = val[1]
                liste_questions_ouv.append((num_question,question,reponse))
            if len(liste_questions_ouv) > 0:    
                self.f.repeating_panel_formul_suivi_questions_ouvertes.visible = True
                self.f.repeating_panel_formul_suivi_questions_ouvertes.items = liste_questions_ouv
        else:
            self.f.repeating_panel_formul_suivi_questions_ouvertes.visible = False
        
        # QUESIONS FERMEES formulaires de suivi
        if self.f.repeating_panel_formul_suivi_questions_fermees.visible is False:
            liste_questions_ferm=[]
            # dico questions ouvertes
            dico_rep_ferm = self.item["rep_dico_rep_ferm"]  # dico questions ouvertes du formulaire
            # Boucle sur le dictionaire ouvert du formulaire
            for cle, val in dico_rep_ferm.items():
                num_question = cle
                question = val[0]
                reponse = val[1]
                liste_questions_ferm.append((num_question,question,reponse))
            if len(liste_questions_ferm) > 0:    
                self.f.repeating_panel_formul_suivi_questions_fermees.visible = True
                self.f.repeating_panel_formul_suivi_questions_fermees.items = liste_questions_ferm
            self.button_download.visible = True
        else:
            self.f.repeating_panel_formul_suivi_questions_fermees.visible = False

    def button_download_click(self, **event_args):
        """This method is called when the button is clicked"""
        # récup du formulaire_row
        formulaire_row = self.item
        # récup du stage
        stage_row = self.item['stage_row']
        
        # role = "T" / "S"
        try:
            role = self.item['user_email']['role']
        except:
            # formulaire anonyme
            role = "S"
            
        # type de formlaire: "suivi" / "fin"  je suis en formulaire de suivi de stage
        type = "suivi"
        try:
            pdf=anvil.server.call("enquete_1_personne_pdf_gen", formulaire_row, stage_row, role, type)
        except Exception as e:
            alert(f"Erreur en génération du PDF (via uplink): {e}")

        # lecture de la date, qui est en str
        date_str =  self.item['date_heure'][0:10]   
        # Conversion du str en objet datetime
        from datetime import datetime
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        # Formatage en chaîne de caractères lisible
        date_ok = date_obj.strftime("%d/%m/%Y")
        
        # lecture du nom, prénom de l'auteur du formulaire 
        try:
            auteur_row = app_tables.users.get(email=self.item['user_email'])
            nom = auteur_row['nom']
            prenom = auteur_row['prenom']
            file_name=(f"Formulaire_Fin_Stage_{self.item['stage_type_txt']}_{nom}_{prenom}_rempli_le_{date_ok} ")
        except Exception as e:
            print(f"Erreur non blocante en relecture de l'auteur du formulaire de suivi: {e}")
            file_name=(f"Formulaire_Fin_Stage_{self.item['stage_type_txt']}_rempli_le_{date_ok}")
        
        new_file_named = anvil.BlobMedia("application/pdf", pdf.get_bytes(), name=file_name+".pdf")
        anvil.media.download(new_file_named)
        