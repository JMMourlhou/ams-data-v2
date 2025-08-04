from anvil import *
import anvil.files
from anvil.files import data_files
import anvil.email



from anvil.tables import app_tables
#import tables
#from tables import app_tables




import anvil.users
import anvil.server
from anvil.http import url_encode
import bcrypt

import uuid   # this library generates codes (API keys for exemple)
import sys
from . import French_zone # importation du module pour le calcul du jour / heure du sign in

from . import var_globales # importation du module contenant la variable globale mon logo (a anuler qd j'ai trouvé ce qui ne va pas)
from datetime import datetime
from . import Variables_globales
# variables globales du modules qui contiendront les var_globales de l'appli
# voir le dernier module recup_global_variables():
global code_app2
code_app2 = ""
global code_app1
code_app1 = ""
global nom_app_pour_mail
nom_app_pour_mail = ""
global mon_mail
mon_mail = ""
global mon_logo      # A AJOUTER PLUS TARD, pour l'instant, ne fonctionne pas
mon_logo = ""



# Forcer login de l'utilisateur qui se connecte    
@anvil.server.callable
def force_log(user_row):
    user=anvil.users.force_login(user_row,remember=True)
    user["last_login"]=French_zone.french_zone_time()  # Update the login time
    return user

""" demande de chgt de Password """    
@anvil.server.callable
def _send_password_reset(email):
    """Send a password reset email to the specified user"""
    global code_app2, code_app1, nom_app_pour_mail, mon_mail, mon_logo
    recup_global_variables()   # appel au module qui va lire les var_globales, stockées ds table 'Global_variables'
    
    user = app_tables.users.get(email=email)
    t=recup_time() # t will be text form (module at the end of this server code module)
    if user is not None:
        #logo_address = code_app1+"/_/theme/"+var_globales.mon_logo
        logo_address = code_app1 + "/_/theme/" + mon_logo
        print(f"adresse du logo: {logo_address}")
        anvil.email.send(to=user['email'], subject=nom_app_pour_mail + "Réinitialisez votre mot de passe",
                         html=f"""
<p><img src = {logo_address} width="200" height="200"> </p> 
<b>Mme/Mr {user["nom"]},</b><br>
<br>
Avez-vous bien demandé une modification du mot de passe de votre compte ? Si ce n'est pas vous, supprimez cet email ! <br>
<br>
Si vous désirez poursuivre et ré-initialiser votre mot de passe, <b>clickez le lien ci-dessous:</b>
<br>

{code_app1}/#?a=pwreset&email={url_encode(user['email'])}&api={url_encode(user['api_key'])}&t={t} <br>
<br><br>
<b><i>         Jean-Marc</b></i>,<br>
https://jmarc@jmm-formation-et-services.fr <br>
JM WEB SERVICES
mail: {mon_mail} <br>
""")

        return True



"""Envoi du mail de confirmation: le mail du new user doit être confirmé"""
@anvil.server.callable
def _send_email_confirm_link(email):
    recup_global_variables()   # appel au module qui va lire les var_globales, stockées ds table 
    global code_app2, code_app1, nom_app_pour_mail, mon_mail

    user = app_tables.users.get(email=email)
    logo_address = code_app1+"/_/theme/"+var_globales.mon_logo
    t=recup_time() # t will be text form (module at the end of this server code module)
    if user is not None and not user['confirmed_email']:  # User table, Column confirmed_email not checked/True
        anvil.email.send(to=user['email'], subject=nom_app_pour_mail + "Confirmation de votre adresse email",
                         html=f"""
<p><img src = {logo_address} width="200" height="200"> </p> 
<b>Mme/Mr {user["nom"]},</b><br>
<br>
Merci de votre enregistrement sur {nom_app_pour_mail} !<br>
Afin de confirmer votre adresse mail, <b>clickez le lien ci-dessous:</b><br>
<br>
{code_app1}/#?a=confirm&email={url_encode(user['email'])}&hpw={url_encode(user['password_hash'])}&t={t} <br>
<br><br>
<b><i>         Jean-Marc</b></i>,<br>
JM WEB SERVICES
https://jmarc@jmm-formation-et-services.fr <br>
mail: {mon_mail} <br>
""")
    return True

""" Création de la clef API si non déjà créée"""
def mk_api_key():
    user_api_key = str(uuid.uuid4())   # Création de l'identifiant unique et transformation en chaîne
    #print(f"UUID  généré: {user_api_key}")
    return user_api_key


"""
# Add the user in a transaction, to make sure there is only ever one user in this database
# with this email address. The transaction might retry or abort, so wait until after it's
# done before sending the email.
"""
@anvil.server.callable
@anvil.tables.in_transaction
def do_signup(email, name, password, num_stage, pour_stage="0"):
    print(email, name, password, num_stage)
    pwhash = hash_password(password, bcrypt.gensalt())
    print("add_user_if_missing email : ", email)  

    user = app_tables.users.get(email=email)
    if user is None:   # user not created yet
        print("non existant")   
        api = mk_api_key()
        date_heure = French_zone.french_zone_time()
        role_user ="S"  # stagiaire par défaut
        num = int(num_stage)
        if num_stage is not None or num_stage != "":
            if num > 999:
                role_user = "F"
            if num == 1003:  # Tuteur
                role_user = "T"
                
        user = app_tables.users.add_row(email=email.lower(),role=role_user, enabled=True, nom=name, password_hash=pwhash, api_key=api, signed_up=date_heure, temp=int(num_stage), temp_for_stage=int(pour_stage))
        print("création user", user['email'])
        err = None # pas d'erreur
    else:  # erreur 
        print("existant",user['email']) 
        err = "Cet adresse mail est déjà enregistrée par nos services. Essayez plutôt de vous connecter."
    return err



# for Pw reset or new user email confirmation  
# is the Api key in URL matches the table API     
def get_user_if_key_correct(email, api_key):
  user_row = app_tables.users.get(email=email)
  if user_row is not None and user_row['api_key'] is not None:
    # Use bcrypt to hash the api key and compare the hashed version.
    # The naive way (api_key == user['api_key']) would expose a timing vulnerability.
    salt = bcrypt.gensalt()
    if hash_password(api_key, salt) == hash_password(user_row['api_key'], salt):
      return True, user_row
  else:
      print("Le mail n'existe pas dans la table users")
      return False, None




# is the Api key in URL matches the table API
@anvil.server.callable
def _is_password_key_correct(email, api_key):
  test_2api_identical = False  
  test_2api_identical = get_user_if_key_correct(email, api_key)
  return test_2api_identical  #True if 2 apis identicals




""" ************************************************************************** """
"""     PASS WORD RESET                                                        """    
""" ************************************************************************** """
@anvil.server.callable
def _perform_password_reset(email, api_key, new_password):
  """Perform a password reset if the key matches; return True if it did."""
  bool, user_row = get_user_if_key_correct(email, api_key)
  if bool:  #user exists, I log him
    user_row['password_hash'] = hash_password(new_password, bcrypt.gensalt())
    return True
 

def hash_password(password, salt):
    """Hash the password using bcrypt in a way that is compatible with Python 2 and 3."""
    if not isinstance(password, bytes):
        password = password.encode()
    if not isinstance(salt, bytes):
        salt = salt.encode()

    result = bcrypt.hashpw(password, salt)

    if isinstance(result, bytes):
        return result.decode('utf-8')


""" ************************************************************************** """
"""         NEW USER: MAIL CONFIRMATION                                         """    
""" ************************************************************************** """
@anvil.server.callable
def _confirm_email_address(email, api_key):
  """Confirm a user's email address if the api key matches; return True if it did."""
  bool=False  
  bool, user_row = get_user_if_key_correct(email, api_key)
  if bool:
    user=anvil.users.get_user()  
    user['confirmed_email'] = True
    #user['api_key'] = None
    anvil.users.force_login(user)
  return bool



def recup_time(): 
    time=French_zone.french_zone_time()
    time_str=""
    time_str=str(time)
    time_str=time_str.replace(" ","_")
    return(time_str)

def recup_global_variables():
    dict={}
    dict = anvil.server.call('get_variable_names')   # in AMS_Data V2
    global code_app2
    #code_app2 = dict["code_app2"]
    
    global code_app1
    code_app1 = dict["code_app1"]
     
    global nom_app_pour_mail
    nom_app_pour_mail = dict["nom_app_pour_mail"]
    
    global mon_mail
    mon_mail = dict["mon_mail"]
    
    global mon_logo
    mon_logo = dict["mon_logo"]