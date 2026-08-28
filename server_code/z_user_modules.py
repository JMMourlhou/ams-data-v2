from anvil import *
import anvil.secrets
import anvil.files
from anvil.files import data_files
import anvil.email

from anvil.tables import app_tables

import anvil.users
import anvil.server
from anvil.http import url_encode
import bcrypt
import uuid   # this library generates codes (API keys for exemple)
import sys
from . import French_zone # importation du module pour le calcul du jour / heure du sign in

from datetime import datetime, timedelta
from . import Variables_globales # importation du module de lecture des variables globales (de la table Variables_globales) 

"""
# Forcer login de l'utilisateur qui se connecte    
@anvil.server.callable
def force_log(user_row):
    user=anvil.users.force_login(user_row,remember=True)
    user["last_login"]=French_zone.french_zone_time()  # Update the login time
    return user
"""


""" demande de chgt de Password """    
@anvil.server.callable
def _send_password_reset(email):
    """
    Envoie un lien permettant de réinitialiser le mot de passe.

    Le token généré :
    - est spécifique au reset du mot de passe ;
    - possède une date d'expiration ;
    - sera invalidé après utilisation.
    """

    # Normalisation de l'adresse mail
    if email is None:
        return True

    email = email.strip().lower()

    user = app_tables.users.get(email=email)

    # Ne pas indiquer au client si l'adresse existe réellement.
    # Cela évite de permettre la recherche d'adresses connues d'AMSdata.
    if user is None:
        print(
            "Demande de réinitialisation pour une adresse inconnue."
        )
        return True

    # Variables utilisées pour le mail
    dict_var_glob = Variables_globales.get_variable_names()

    ams_mail = dict_var_glob["ams_mail"]
    code_app1 = dict_var_glob["code_app1"]

    en_tete_address = (
        code_app1
        + "/_/theme/"
        + dict_var_glob["ams_en_tete"]
    )

    # Création d'un nouveau token de reset
    password_reset_key = mk_password_reset_key()

    # Le lien sera valable 30 minutes
    password_reset_delay_in_minutes = 30

    password_reset_expires = (
        French_zone.french_zone_time()
        + timedelta(minutes=password_reset_delay_in_minutes)
    )

    # Enregistrement côté serveur
    user["password_reset_key"] = password_reset_key
    user["password_reset_expires"] = password_reset_expires

    # Date conservée dans l'URL pour ton contrôle client actuel.
    # Ce n'est pas elle qui assurera désormais la sécurité.
    t = recup_time()

    anvil.email.send(
        to=user["email"],
        subject="Réinitialisez votre mot de passe",
        html=f"""
<p><img src={en_tete_address} width="772" height="263"></p>

<b>Mme/Mr {user["nom"]},</b><br>
<br>

Avez-vous bien demandé une modification du mot de passe de votre compte ?
Si ce n'est pas vous, supprimez cet email.<br>
<br>

Si vous désirez poursuivre et réinitialiser votre mot de passe,
<b>cliquez sur le lien ci-dessous :</b><br>
<br>

{code_app1}/#?a=pwreset&email={url_encode(user["email"])}&api={url_encode(password_reset_key)}&t={t}

<br><br>

<b><i>L'équipe d'AMSport</i></b><br>
mail : {ams_mail}<br>
"""
    )

    return True



"""Envoi du mail de confirmation: le mail du new user doit être confirmé"""
@anvil.server.callable
def _send_email_confirm_link(email):
    # Récupération des variables globales utilisées ici
    dict_var_glob = Variables_globales.get_variable_names()   # var_globale du mail d'AMS, stockées ds table 
    ams_mail = dict_var_glob["ams_mail"]   # var globale Mail AMS
    code_app1 = dict_var_glob["code_app1"]      # var_globale de l'apli AMS DATA
    en_tete_address = code_app1+"/_/theme/"+ dict_var_glob["ams_en_tete"]
    nom_app_pour_mail = dict_var_glob["nom_app_pour_mail"]
    
    user = app_tables.users.get(email=email)
    t=recup_time() # t will be text form (module at the end of this server code module)
    if user is not None and not user['confirmed_email']:  # User table, Column confirmed_email not checked/True
        anvil.email.send(to=user['email'],
                         subject="Confirmation de votre adresse email",
                         from_address = "jmarc@jmm-formation-et-services.fr",
                         from_name = "AMSport",
                         html=f"""
<p><img src = {en_tete_address} width="772" height="263"> </p> 
<b>Mme/Mr {user["nom"]},</b><br>
<br>
Merci de votre enregistrement sur {nom_app_pour_mail} !<br>
Afin de confirmer votre adresse mail, <b>clickez le lien ci-dessous:</b><br>
<br>
{code_app1}/#?a=confirm&email={url_encode(user['email'])}&api={url_encode(user['api_key'])}&t={t} <br>
<br><br>
<b><i>         L'équipe d'AMSport,</b></i><br>
mail: {ams_mail} <br>
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
    print(f"Module 'z_user_modules / do_sign_up': création du user:{email}, {name}, stage {num_stage} pour le stage {pour_stage}")
    
    # Le contrôle coté client est utile pour l'utilisateur, mais il peut être contourné par un attaquant, donc on répète le test en serveur
    # Le mot de passe doit obligatoirement être renseigné.
    if password is None:
        return "Le mot de passe est obligatoire."
    
    if password == "":
        return "Le mot de passe est obligatoire."

    if len(password) < 6:
        return "Le mot de passe doit contenir au minimum 6 caractères."
    
    pwhash = hash_password(password, bcrypt.gensalt())
    user = app_tables.users.get(email=email)
    if user is None:   # user not created yet
        api = mk_api_key()
        date_heure = French_zone.french_zone_time()
        # Tout utilisateur qui crée lui-même son compte est créé
        # avec le rôle stagiaire par défaut.
        # Le rôle pourra être modifié ultérieurement par une opération contrôlée.
        role_user ="S"  # stagiaire par défaut
        """
        if num_stage is not None or num_stage != "":
            # lecture du stage sur son num(numéric)
            try:
                stage_row=app_tables.stages.get(numero=int(num_stage))
                role_user = stage_row["type_stage"]
                print(f"Module 'z_user_modules / do_sign_up': Stage {num_stage} bien lu ***")
                print(f"Module 'z_user_modules / do_sign_up': rôle du user: {role_user}")
            except Exception as e:
                print(f"Module 'z_user_modules / do_sign_up': création du user: *** erreur en inscription au stage ({num_stage}) à attribuer pour ce nouvel user *** , role='S' par défaut")
                print(e)
                print("------------------------------------")
                role_user = "S" # par défaut
        """
        try:        
            user = app_tables.users.add_row(email=email.lower(),
                                            role=role_user,
                                            enabled=True,
                                            nom=name,
                                            password_hash=pwhash,
                                            api_key=api,
                                            signed_up=date_heure,
                                            temp=int(num_stage),
                                            temp_for_stage=int(pour_stage)
                                           )
            print("création user", user['email'])
            err = None # pas d'erreur
        except Exception as e:
            return e
    else:  # erreur 
        print(f"Module 'z_user_modules / do_sign_up', en création du user, son adresse mail {user['email']} déjà existante ! ") 
        err = "Cette adresse mail est déjà connue... Essayez de vous connecter."
    return err



# for Pw reset or new user email confirmation  
# is the Api key in URL matches the table API     
def get_user_if_key_correct(email, api_key):
    user_row = app_tables.users.get(email=email)

    if user_row is None:
        print("Le mail n'existe pas dans la table users")
        return False, None

    if user_row["api_key"] is None:
        return False, None

    if api_key is None:
        return False, None

    # Comparaison des deux clés
    salt = bcrypt.gensalt()

    api_key_hash = hash_password(
        api_key,
        salt
    )

    user_api_key_hash = hash_password(
        user_row["api_key"],
        salt
    )

    if api_key_hash == user_api_key_hash:
        return True, user_row

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
def _perform_password_reset(email, password_reset_key, new_password):
    """
    Réinitialise le mot de passe si :
    - le token est valide ;
    - le token n'est pas expiré ;
    - le nouveau mot de passe respecte les règles.

    Le token est supprimé immédiatement après utilisation.
    """

    # Validation du nouveau mot de passe côté serveur
    if new_password is None:
        return False

    if new_password == "":
        return False

    password_min_length = 6

    if len(new_password) < password_min_length:
        return False

    # Vérification du token
    key_is_correct, user_row = (
        get_user_if_password_reset_key_correct(
            email,
            password_reset_key
        )
    )

    if not key_is_correct:
        return False

    # Modification du mot de passe
    user_row["password_hash"] = hash_password(
        new_password,
        bcrypt.gensalt()
    )

    # Réinitialisation du compteur de mots de passe erronés
    user_row["n_password_failures"] = 0
    
    # Invalidation immédiate du lien de reset
    user_row["password_reset_key"] = None
    user_row["password_reset_expires"] = None

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
    """
    Confirme l'adresse mail d'un utilisateur si la clé reçue
    correspond à celle enregistrée dans la table users.

    Entrées :
        email : str
        api_key : str

    Sortie :
        True si la confirmation a réussi.
        False dans le cas contraire.
    """

    key_is_correct, user_row = get_user_if_key_correct(
        email,
        api_key
    )

    if not key_is_correct:
        return False

    # Confirmation de l'adresse mail
    user_row["confirmed_email"] = True

    # Création d'une nouvelle clé.
    # L'ancien lien de confirmation devient ainsi inutilisable.
    user_row["api_key"] = mk_api_key()

    # Connexion de l'utilisateur dont le mail vient d'être confirmé
    anvil.users.force_login(user_row)

    return True

def recup_time(): 
    time=French_zone.french_zone_time()
    time_str=""
    time_str=str(time)
    time_str=time_str.replace(" ","_")
    return(time_str)

def mk_password_reset_key():
    """
    Génère une clé unique utilisée uniquement
    pour la réinitialisation du mot de passe.
    """
    password_reset_key = str(uuid.uuid4())
    return password_reset_key

def get_user_if_password_reset_key_correct(email, password_reset_key):
    """
    Vérifie :
    - que l'utilisateur existe ;
    - que le token existe ;
    - que le token correspond ;
    - que le délai n'est pas dépassé.

    Retour :
        True, user_row
        ou
        False, None
    """

    if email is None:
        return False, None

    if password_reset_key is None:
        return False, None

    email = email.strip().lower()

    user_row = app_tables.users.get(email=email)

    if user_row is None:
        return False, None

    stored_password_reset_key = user_row["password_reset_key"]
    password_reset_expires = user_row["password_reset_expires"]

    if stored_password_reset_key is None:
        return False, None

    if password_reset_expires is None:
        return False, None

    # Contrôle de l'expiration côté serveur
    time_now = French_zone.french_zone_time()

    if time_now > password_reset_expires:
        # Le token expiré est supprimé.
        user_row["password_reset_key"] = None
        user_row["password_reset_expires"] = None

        return False, None

    # Comparaison du token reçu avec celui enregistré.
    if password_reset_key != stored_password_reset_key:
        return False, None

    return True, user_row

@anvil.server.callable
def _password_reset_link_is_valid(email, password_reset_key):
    """Vérifie si un lien de réinitialisation peut encore être utilisé."""

    if email is None or password_reset_key is None:
        return False

    email = email.strip().lower()
    user_row = app_tables.users.get(email=email)

    if user_row is None:
        return False

    stored_password_reset_key = user_row["password_reset_key"]
    password_reset_expires = user_row["password_reset_expires"]

    if stored_password_reset_key is None or password_reset_expires is None:
        return False

    if French_zone.french_zone_time() > password_reset_expires:
        user_row["password_reset_key"] = None
        user_row["password_reset_expires"] = None
        return False

    if password_reset_key != stored_password_reset_key:
        return False

    return True    