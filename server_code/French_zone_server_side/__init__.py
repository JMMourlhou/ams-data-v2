import anvil.email

import anvil.files
from anvil.files import data_files

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from pytz import timezone
from datetime import datetime

#Get the time now, local time FOR servor SIDE (no time from browser)
def time_french_zone():
    now_utc = datetime.now(timezone('UTC'))
    date_time = now_utc.astimezone(timezone('Europe/Paris')) # initialisation of the date & time of writing
    return date_time

