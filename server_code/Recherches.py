import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

    
# ================================================== RECHERCHES
@anvil.server.callable
def search_on_name_only(critere):
    liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        nom    = q.ilike(critere),    # ET
                                    )
    return liste

@anvil.server.callable
def search_on_prenom_only(critere):
    liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                       
                                        prenom    = q.ilike(critere),    # ET
                                    )
    return liste

@anvil.server.callable
def search_on_role_only(critere):
    liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        role   = q.ilike(critere)
                                    )
    return liste

@anvil.server.callable
def search_on_role_nom(c_role, c_nom):
    liste = app_tables.users.search(    q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        q.all_of                  # all of queries must match
                                        (
                                            role   = q.ilike(c_role),   # ET
                                            nom    = q.ilike(c_nom)   
                                        )
                                    )
    return liste

@anvil.server.callable
def search_on_nom_prenom(c_nom, c_prenom):
    liste = app_tables.users.search(    q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        q.all_of                  # all of queries must match
                                        (
                                            prenom   = q.ilike(c_prenom),   # ET
                                            nom    = q.ilike(c_nom)   
                                        )
                                    )
    return liste

@anvil.server.callable
def search_on_role_nom_prenom(c_role, c_nom, c_prenom):
    liste = app_tables.users.search(    q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("nom", ascending=True),
                                        q.all_of                  # all of queries must match
                                        (
                                            role   = q.ilike(c_role),   # ET
                                            prenom   = q.ilike(c_prenom),   # ET
                                            nom    = q.ilike(c_nom)   
                                        )
                                    )
    return liste

@anvil.server.callable
def search_on_tel_only(critere):
    liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("tel", ascending=True),
                                        tel   = q.ilike(critere)
                                    )
    return liste

@anvil.server.callable
def search_on_email_only(critere):
    liste = app_tables.users.search(
                                        q.fetch_only("nom","prenom","email","tel","role"),
                                        tables.order_by("email", ascending=True),
                                        email   = q.ilike(critere)
                                    )
    return liste
