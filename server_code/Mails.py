import anvil.email
import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import French_zone_server_side

global timing
timing = French_zone_server_side.time_french_zone()
print(f"time: {timing}")

@anvil.server.callable
def add_mail_model(row_type,
                    subject,
                    text
                    ):
    
    row = app_tables.mail_templates.add_row(
                    type = row_type,
                    mail_subject = subject,
                    mail_text = text,
                    last_modif_date = timing
                            )
    if row:
        return True
    else:
        return False


@anvil.server.callable
def modify_mail_model(id,
                subject,
                text
                ):
    print("id: ",id)
    # finding the mail's row 
    row=tables.app_tables.mail_templates.get_by_id(id)
    if not row:
        print("Erreur: mail non trouvé en modif !")
        return False
    else:           
        row.update(mail_subject = subject,
                   mail_text = text,
                   last_modif_date = timing
                            )
        return True

@anvil.server.callable
def del_mails(id):
    # finding the mail's row 
    row=tables.app_tables.mail_templates.get_by_id(id)
    
    if not row:
        print("Erreur: mail non trouvé en deletion !")
        return False
    else:           
        row.delete()
        return True