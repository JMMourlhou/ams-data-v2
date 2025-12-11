import anvil.email
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import *  #pour les alertes


# =========================================================================================
# appelé par form Evenements 
# Création d'un nouvel Evenement (Réunion ou Incident), sauvegarde auto tt les 15 secondes...
#   ... pour éviter de perdre les données en cas de session expired (sur tel possible)

@anvil.server.callable 
# Auto_sov = True: sauvegarde auto, doit modifier le row, si un id existe déjà
# id du row = not None si sauvegarde auto, contient le id_row à modifier (sauf si c'est la 1ere sauvegarde)
# auto_sov  = # False si bt validation utilisé   /   True si sauvegarde auto lancée par timer2, ts les 15 secondes
def add_event(id, auto_sov, type_event, row, date_time, lieu_row, lieu_txt, note, img_1, img_2, img_3, writing_date_time, mot_clef):
    
    #   id = None, indique que c'est une premiere sauvegarde, j'utilise .add_row
    if id is None:
        try:
            new_row=app_tables.events.add_row(  
                                                auto_sov=auto_sov,      # si c'est une sauvegarde automatique ts les 15 sec, le tag auto_sov est à True
                                                type_event=type_event,
                                                event_typ=row,
                                                date=date_time,
                                                lieu=lieu_row,
                                                lieu_text=lieu_txt,
                                                note=note,
                                                img1=img_1,
                                                img2=img_2,
                                                img3=img_3,
                                                writing_date_time=writing_date_time,
                                                mot_clef=mot_clef
                                            )
        except Exception as e:
            return e, None   # erreur je retourne l'exception et la deuxiemevariable attendue (l'id) à None
            
        id = new_row.get_id()  # en création de l'évènement, je sauve l'id pour pouvoir le modifier en sauvegrde auto ou sauvegarde finale (bt Validation)
        re_read_row = app_tables.events.get_by_id(id)
        if re_read_row:
            valid=True
        else:
            valid=False
        
    # si id = not None, indique qu'il y a déjà eu une sauvegarde: j'utilise update
    if id is not None:
        try:
            re_read_row = app_tables.events.get_by_id(id)
            valid=True
        except Exception as e:
            return e, id
            
        if re_read_row:
            try:
                re_read_row.update(
                                    auto_sov=auto_sov,      # si c'est une sauvegarde automatique ts les 15 sec, le tag auto_sov est à True
                                    type_event=type_event,
                                    date=date_time,
                                    lieu=lieu_row,
                                    lieu_text=lieu_txt,
                                    note=note,
                                    img1=img_1,
                                    img2=img_2,
                                    img3=img_3,
                                    writing_date_time=writing_date_time,
                                    mot_clef=mot_clef
                                    )
                valid=True
            except Exception as e:
                return e, id
    return valid, id


# =========================================================================================
# appelé par form Evenements_vissu_modif_del / ItemTemplate21
# Effacement d'un Evenement (Réunion ou Incident)
# row contient le self.item à effacer, (click sur bt del)
@anvil.server.callable 
def del_event(to_be_deleted_event_row):
    result=False
    id=to_be_deleted_event_row.get_id()
    to_be_deleted_event_row.delete()
    print("effacement du row effectué normalement")

    #relecture
    test = app_tables.events.get_by_id(id)
    if not test:
        result=True
    return result

# =========================================================================================
# appelé par form Evenements    BT Retour alors qu'il ya eu sauvegarde temp
# Effacement de l'Evenement (Réunion ou Incident)
# id du row à effacer
@anvil.server.callable 
def del_event_bt_retour(id):
    result=False
    to_be_deleted_row = app_tables.events.get_by_id(id)
    to_be_deleted_row.delete()
    print("effacement du row temporaire après Bt Retour")

    #relecture
    test = app_tables.events.get_by_id(id)
    if not test:
        result=True
    return result

# =========================================================================================
# appelé par form Evenements_MAJ_table    
# Création d'un nouveau type d'évenemnts
@anvil.server.callable 
def add_type_evnt(type_evnt,             # text
                  code,                  # NUMBER
                  msg_0,                  # text
                  msg_1,                  # text
                  text_initial,          # text
                  mot_clef_avec_date     # True / False
                 ):
    new_row=app_tables.event_types.add_row(
                                            type =           type_evnt,             # text
                                            code =           code,                  # NUMBER 
                                            msg_0 =          msg_0,                  # text
                                            msg_1 =          msg_1,                  # text
                                            text_initial =   text_initial,          # text
                                            mot_clef_setup = mot_clef_avec_date     # True / False    
                                        )
    id = new_row.get_id()  # en création de l'évènement, je sauve l'id pour pouvoir le modifier en sauvegrde auto ou sauvegarde finale (bt Validation)
    re_read_row = app_tables.event_types.get_by_id(id)
    if re_read_row:
        valid=True
    else:
        valid=False
    return valid


# =========================================================================================
# appelé par form Evenements_MAJ_table  
# Création d'un nouveau type d'évenemnts
@anvil.server.callable 
def modif_type_evnt(row,
                  type_evnt,             # text
                  code,                  # NUMBER
                  msg_0,                  # text
                  msg_1,                  # text
                  text_initial,          # text
                  mot_clef_avec_date     # True / False
                 ):
    valid= False
    #print(f"text_initial: {text_initial}")
    row.update(
                type =           type_evnt,             # text
                code =           code,                  # NUMBER 
                msg_0 =          msg_0,                  # text
                msg_1 =          msg_1,                  # text
                text_initial =   text_initial,          # text
                mot_clef_setup = mot_clef_avec_date     # True / False    
                )
    valid = True
    #print(f"text_initial: {row['text_initial']}")
    return valid

# =========================================================================================
# appelé par form Evenements_MAJ_table
# Effacement d'un type d'Evenement (Réunion, Incident, ...)
@anvil.server.callable 
def del_type_evnt(row):
    id = row.get_id()
    result=False
    row.delete()
    
    #relecture
    test = app_tables.event_types.get_by_id(id)
    if not test:
        result=True
    return result