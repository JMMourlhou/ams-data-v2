import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

"""
Ce module teste s'il ya des users qui ont eu 5 failures en essayant de rentrer ds l'app
Testé dans init de Main si le suser est admin
"""
def test_pw_failures():
    try:
        liste= list(app_tables.users.search(n_password_failures = q.greater_than_or_equal_to(10)))
        return True, liste
    except Exception as e:
        return False, e
    