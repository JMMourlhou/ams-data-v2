from ._anvil_designer import ItemTemplate20Template
from anvil import *
import anvil.server

import anvil.users
import anvil.tables as tables

from anvil.tables import app_tables


class ItemTemplate20(ItemTemplate20Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label_nom.text = self.item['nom']         # Nom stagiaire
        #longueur_voulue = 100
        if self.item['q1'] != "":
            self.label_1.visible = True
            self.label_1.text = self.display(self.item['pourcent_1'])   # fonction displaypour arrondir le % à l'entier
            self.label_1.background = self.bg_couleur(self.item['pourcent_1'])
            
        if self.item['q2'] != "":
            self.label_2.visible = True
            self.label_2.text = self.display(self.item['pourcent_2'])
            self.label_2.background = self.bg_couleur(self.item['pourcent_2'])
            
        if self.item['q3'] != "":
            self.label_3.visible = True
            self.label_3.text = self.display(self.item['pourcent_3'])
            self.label_3.background = self.bg_couleur(self.item['pourcent_3'])
            
        if self.item['q4'] != "":
            self.label_4.visible = True
            self.label_4.text = self.display(self.item['pourcent_4'])
            self.label_4.background = self.bg_couleur(self.item['pourcent_4'])
            
        if self.item['q5'] != "":
            self.label_5.visible = True
            self.label_5.text = self.display(self.item['pourcent_5'])
            self.label_5.background = self.bg_couleur(self.item['pourcent_5'])

        if self.item['q6'] != "":
            self.label_6.visible = True    
            self.label_6.text = self.display(self.item['pourcent_6'])
            self.label_6.background = self.bg_couleur(self.item['pourcent_6'])

        if self.item['q7'] != "":
            self.label_7.visible = True
            self.label_7.text = self.display(self.item['pourcent_7'])
            self.label_7.background = self.bg_couleur(self.item['pourcent_7'])
        
        if self.item['q8'] != "":
            self.label_8.visible = True
            self.label_8.text = self.display(self.item['pourcent_8'])
            self.label_8.background = self.bg_couleur(self.item['pourcent_8'])

        if self.item['q9'] != "":
            self.label_9.visible = True
            self.label_9.text = self.display(self.item['pourcent_9'])
            self.label_9.background = self.bg_couleur(self.item['pourcent_9'])

        if self.item['q10'] != "":
            self.label_10.visible = True
            self.label_10.text = self.display(self.item['pourcent_10'])
            self.label_10.background = self.bg_couleur(self.item['pourcent_10'])
       
        
    def display(self, nb, **properties):
        nb1=round(nb)
        print(nb1)
        text = str(nb1)+" %"
        print(text)
        return text
        
    def bg_couleur(self, nb):
        if nb < 10 == 0:
            bg_couleur = "theme:Error"
        elif nb < 30:
            bg_couleur = "theme:Orange"    
        elif nb < 60:
            bg_couleur = "theme:Jaune Orange"
        elif nb < 80:
            bg_couleur = "theme:Vert Tres Clair"
        elif nb < 90:
            bg_couleur = "theme:Vert Clair"    
        else:
            bg_couleur = "theme:Vert Foncé"
        return bg_couleur
        

    def space_height(self, question):
        # 1 ligne de texte = 14 caract ds l'outline card
        # 4 lignes = 4*16 = 64
        lg = len(question)
        nb_lignes = int(lg / 19)
        reste = lg % 19
        if reste > 0:
            nb_lignes += 1
        
        if nb_lignes == 1 or nb_lignes == 0:
            space = 32
            print(f"nb de lignes: {nb_lignes} / question: {question} ")
            print(f"space height: {space}")
        elif nb_lignes == 2:
            space = 10
            print(f"nb de lignes: {nb_lignes} / question: {question} ")
            print(f"space height: {space}")
        elif nb_lignes == 3:
            space = 8
            print(f"nb de lignes: {nb_lignes} / question: {question} ")
            print(f"space height: {space}")
        else :
            space = 0
            print(f"nb de lignes: {nb_lignes} / question: {question} ")
            print(f"space height: {space}")
        return space
