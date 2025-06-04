import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.users
import tables
from tables import app_tables
#import anvil.tables as tables
import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
import bcrypt # to test the API key crypted
from . import French_zone

#test3: is the new user in the users data table (for email validation) ?
@anvil.server.callable
def search(to_be_confirmed_email, hpw):
    print(to_be_confirmed_email)
    new_user_row=app_tables.users.get(email=to_be_confirmed_email)
    if new_user_row == None:
        print("user not found")
        return

        #test4: pwh ds lien correspond-il au hpw ds le user row? 
        # Use bcrypt to hash the api key and compare the hashed version.
        # The naive way (hpw == user['api_key']) would expose a timing vulnerability.

    salt = bcrypt.gensalt()
    print("url hpw; ",hpw)
    print("salt; ",salt)

    if hash_password(hpw, salt) != hash_password(new_user_row['password_hash'], salt):
        return
    user=None   
    if new_user_row is not None and not new_user_row['confirmed_email']:  # User table, Column confirmed_email not checked/True
        new_user_row['confirmed_email']=True                              #je mets à jour la column confirmed email
        new_user_row["signed_up"]=French_zone.french_zone_time()
        new_user_row["last_login"]=new_user_row["signed_up"]
        #new_user_row['histo']={}
        # Forcing my new user to login
        user=anvil.users.force_login(new_user_row)
        print(user["nom"])
    return user

def hash_password(password, salt):
    print("password; ", password)
    """Hash the password using bcrypt in a way that is compatible with Python 2 and 3."""
    if not isinstance(password, bytes):
        password = password.encode()
    if not isinstance(salt, bytes):
        salt = salt.encode()

    result = bcrypt.hashpw(password, salt)

    if isinstance(result, bytes):
        return result.decode('utf-8')