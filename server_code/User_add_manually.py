from anvil import *
import anvil.files
from anvil.files import data_files

from anvil.tables import app_tables

import anvil.users
import anvil.server

import bcrypt
import uuid   # this library generates codes (API keys for exemple)

# Création d'un utilisateur sans procédure (sans validation par mail)
# --> ira dans stage 1009 automatiqt en saisie_info_de_base SI PRENOM EST à Vide

@anvil.server.callable
@anvil.tables.in_transaction
def new_user(nom, prenom, tel, email, role, signed_up, temp=None, temp_for_stage=None):
    err = None
    print(email, nom)
    
    user = app_tables.users.get(email=email)
    if user is None:   # user not created yet
        print("non existant")   
        pwhash = hash_password("ams2026", bcrypt.gensalt())
        api = str(uuid.uuid4())   # Création de l'identifiant unique et transformation en chaîne
        
        user = app_tables.users.add_row(email=email.lower(),
                                        role=role,
                                        enabled=True,
                                        confirmed_email=True,
                                        nom=nom,
                                        prenom=prenom,
                                        tel=tel,
                                        password_hash=pwhash,
                                        api_key=api,
                                        signed_up=signed_up,
                                        temp=int(temp) if temp is not None else None,
                                        temp_for_stage=int(temp_for_stage) if temp_for_stage is not None else None
                                       )
        print("création user", user['email'])
    else:  # erreur 
        print("existant",user['email']) 
        err = "Cet adresse mail est déjà enregistrée !"
    return err

def hash_password(password, salt):
    """Hash the password using bcrypt in a way that is compatible with Python 2 and 3."""
    if not isinstance(password, bytes):
        password = password.encode()
    if not isinstance(salt, bytes):
        salt = salt.encode()

    result = bcrypt.hashpw(password, salt)

    if isinstance(result, bytes):
        return result.decode('utf-8')    

