from ._anvil_designer import Users_searchTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Users_search(Users_searchTemplate):
    def __init__(self, modif="", **properties):   # modif si reviens de modif from Template7
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.data_grid_1.visible = True
        
       
        self.modif = modif
        #alert(f"en entrée forme principale: self.modif: {self.modif}")
        if self.modif=="":
            self.text_box_role_focus()
        if self.modif=="enabled":
            self.check_box_enabled.checked = True
            self.check_box_enabled_change()
        if self.modif=="confirmation":
            self.check_box_confirmed_mail.checked = True
            self.check_box_confirmed_mail_change()
            
    def button_annuler_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..Main import Main
        open_form("Main", 99)

    def text_box_role_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""

        # Initialisation de l'affichage par role
        critere = self.text_box_role.text + "%"            #  wildcard search on role
        liste = app_tables.users.search(tables.order_by("role", ascending=True),
                                        role=q.ilike(critere),
                                                )
        self.repeating_panel_1.items=liste

    def text_box_nom_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""
        
        critere = self.text_box_nom.text + "%"            #  wildcard search on date
        liste = app_tables.users.search(tables.order_by("nom", ascending=True),
                                        nom=q.ilike(critere)
                                                )
        self.repeating_panel_1.items=liste

    def text_box_prenom_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_mail.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""
        
        critere = self.text_box_prenom.text + "%"            #  wildcard search on date
        liste = app_tables.users.search(tables.order_by("prenom", ascending=True),
                                        prenom=q.ilike(critere)
                                                )
        self.repeating_panel_1.items=liste

    def text_box_mail_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""
        
        critere = self.text_box_mail.text + "%"            #  wildcard search on date
        liste = app_tables.users.search(tables.order_by("email", ascending=True),
                                        email=q.ilike(critere)
                                                )
        self.repeating_panel_1.items=liste   

    def text_box_pw_failure_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""
        
        liste = app_tables.users.search(tables.order_by("n_password_failures", ascending=False),
                                       enabled=True)        
        self.repeating_panel_1.items=liste   

    def text_box_sign_up_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_connexion.text = ""

        liste = app_tables.users.search(tables.order_by("signed_up", ascending=False),
                                        enabled=True)  
        self.repeating_panel_1.items=liste   

    def text_box_connexion_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.check_box_confirmed_mail.checked = False
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""

        liste = app_tables.users.search(tables.order_by("last_login", ascending=False),
                                        enabled=True)  
        self.repeating_panel_1.items=liste  
    
    def check_box_confirmed_mail_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_enabled.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""
        
        if self.check_box_confirmed_mail.checked is True:
            # cas ou col contient None (qd inscription par qr code s'est pa bien déroulée)
            # (mais pourrait peut-être contenir False)
            critere = None            
            liste1 = app_tables.users.search(tables.order_by("nom", ascending=True),
                                            confirmed_email=critere
                                                    )
            
            critere = False           
            liste2 = app_tables.users.search(tables.order_by("nom", ascending=True),
                                            confirmed_email=critere
                                                    )
            
            liste = list(liste1) + list(liste2) 
            self.repeating_panel_1.items=liste
        else:
            self.text_box_nom_focus()

    def check_box_enabled_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.text_box_role.text = ""
        self.text_box_nom.text = ""
        self.text_box_prenom.text = ""
        self.text_box_mail.text = ""
        self.text_box_pw_failure.text = ""
        self.check_box_confirmed_mail.checked = False
        self.text_box_sign_up.text = ""
        self.text_box_connexion.text = ""
        
        #alert(self.check_box_enabled.checked)
        
        if self.check_box_enabled.checked is True:
            # cas ou col contient False, (mais pourrait peut-être contenir None)
            critere = False
            liste1 = app_tables.users.search(tables.order_by("nom", ascending=True),
                                            enabled=critere
                                                    )
            critere = None
            liste2 = app_tables.users.search(tables.order_by("nom", ascending=True),
                                            enabled=critere
                                                    )
            liste = list(liste1) + list(liste2)
            self.repeating_panel_1.items=liste
        else:
            self.text_box_nom_focus()

    
   

  



   
   