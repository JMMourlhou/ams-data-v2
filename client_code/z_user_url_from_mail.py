""" Read the URL sent by the mail link, after a new user signed in or PW reset"""
from anvil import *   # to load the alert    

import anvil.users
import anvil.tables as tables
import anvil.server
from . import z_user_login_flow

from anvil import open_form

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
    print("type; ", isinstance(h, dict))

    url_purpose=h["a"]  # contient le but du lien: qrcode ou pwrest ou confirm

    """ ***************************** URL crée après que le user ai flaché un qrcode  """
    
    if url_purpose == "qrcode":
        z_user_login_flow.signup_with_form(num_stage)        # envoyer en sign in

    # mail in URL ?
    to_be_confirmed_email=h["email"]
    if to_be_confirmed_email == "" :
        alert("email vide")
        return
    
    """ ***************************** URL du mail de password reset  """
    """ ***************************** URL du mail de password reset  """
    if url_purpose=='pwreset':
        #alert("pwreset, going to form 'url_from_mail_PW_reset'")
        #login_flow.do_email_reset(h)  
        from . url_from_mail_PW_reset import url_from_mail_PW_reset
        open_form("url_from_mail_PW_reset",h["email"],h["api"])

    """ ***************************** URL du mail de confirmation après sign in  """
    if url_purpose=='confirm':
        #alert("confirm")
        # Hash password in URL ?
        hpw=h["hpw"]
        if not hpw:
            alert("Hash Password empty")
            return
        try:   
            #test3: is the user in the users data table ?
            user=anvil.server.call("search", to_be_confirmed_email, hpw)
            #Displaying the confirm alert 
            msg="Mr/Mme "+user["nom"]+", votre mail est confirmé, connectez-vous avec votre mail et mot de passe."
            alert(msg)
        except anvil.users.EmailNotConfirmed:   # pas confirmé ?
            alert("Votre mail est connu par nos services mais n'est pas confirmé, cliquez le dernier lien envoyé par mail.")
        except:  #user confirmé
            #alert("Votre mail est déjà confirmé, essayez de vous connecter.")
            pass

    anvil.users.logout()       #logging out the user
    open_form("Main",99)



# This code displays an Anvil alert, rather than
# the default red box, when an error occurs.
def error_handler(err):
    alert(str(err), title="An error has occurred")    