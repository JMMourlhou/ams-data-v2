import anvil.secrets
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


"""
Ce module teste s'il y a des users qui ont eu 10 failures en essayant de rentrer ds l'app
Testé dans init de Main si le suser est admin
"""
@anvil.server.callable
def test_pw_failures():

    print("Test administrateur: PassWord failures ?")
    try:
        liste = list(app_tables.users.search(n_password_failures = q.greater_than_or_equal_to(10)))
        if len(liste)>0:
            print(f"ATTENTION: {len(liste)} user(s) blocked:")
            for u in liste:
                print(f"{u['prenom']} {u['nom']}, mail: {u['email']}")
        else:
            print("No user blocked !")
        print()
        return True, liste       
    except Exception as e:
        return False, str(e)

def hash_password(password, salt):
    """Hash the password using bcrypt in a way that is compatible with Python 2 and 3."""
    if not isinstance(password, bytes):
        password = password.encode()
    if not isinstance(salt, bytes):
        salt = salt.encode()

    result = bcrypt.hashpw(password, salt)

    if isinstance(result, bytes):
        return result.decode('utf-8')    