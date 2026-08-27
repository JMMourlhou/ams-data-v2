""" Read the URL sent by the mail link, after a new user signed in or PW reset"""
from anvil import *   # to load the alert    
import anvil.users
import anvil.tables as tables
import anvil.server
#from . import z_user_login_flow
from .z_user_new_account import z_user_new_account
from anvil import open_form
from .AlertHTML import AlertHTML
from .AlertConfirmHTML import AlertConfirmHTML

"""In a URL, what travels after # is known as hash.
In an HTTP request that reaches a server (server side)
this data does not travel to the server.
Therefore, on the server side, it is not possible to retrieve it
(web browsers do not send this data in the HTTP request).
However, on the client side it is possible. """  

def confirm_or_pwreset(h, num_stage=0):   
    if h is None:
        print(f"l'Url est vide: {h}")
        return
    to_be_confirmed_email=""

    #test1: si h est type dict
    if not isinstance(h, dict):  
        print("URL not a dict type")
        return

    # Valeurs par défaut
    pour_stage = h.get("pour", 0)
    
    # But du lien : qrcode, pwreset ou confirm
    url_purpose=h["a"]  

    """ ***************************** URL crée après que le user ai flaché un qrcode  """ 
    if url_purpose == "qrcode":
        open_form("z_user_new_account", h, num_stage, pour_stage)
        return
        
    """ ***************************** URL du mail de password reset  """
    if url_purpose=='pwreset':
        #alert("pwreset, going to form 'url_from_mail_PW_reset'")
        #login_flow.do_email_reset(h)  
        from . url_from_mail_PW_reset import url_from_mail_PW_reset
        open_form("url_from_mail_PW_reset",h["email"],h["api"])

    """ ***************************** URL du mail de confirmation après sign in  """
    if url_purpose == "confirm":
        # Lecture du mail contenu dans l'URL
        to_be_confirmed_email = h.get("email")
    
        if not to_be_confirmed_email:
            AlertHTML.error(
                "Erreur :",
                "L'adresse mail est absente du lien de confirmation."
            )
            return
    
        # Lecture de la clé de confirmation contenue dans l'URL
        api_key = h.get("api")
    
        if not api_key:
            AlertHTML.error(
                "Erreur :",
                "Le lien de confirmation est invalide."
            )
            return
    
        # Vérification et confirmation côté serveur
        confirmation_ok = anvil.server.call(
            "_confirm_email_address",
            to_be_confirmed_email,
            api_key
        )
    
        if confirmation_ok:
            AlertHTML.success(
                "Succès",
                "Votre adresse mail est maintenant confirmée."
            )
        else:
            AlertHTML.error(
                "Erreur :",
                "Ce lien de confirmation n'est pas valide."
            )
    
        open_form("Main", 99)
        return



# This code displays an Anvil alert, rather than
# the default red box, when an error occurs.
def error_handler(err):
    alert(str(err), title="An error has occurred")    