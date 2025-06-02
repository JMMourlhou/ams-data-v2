
import anvil.server

import anvil.tables as tables
# Pour le calcul de l'heure en France
from anvil import *  #pour les alertes
import anvil.tz
# Pour le calcul de l'heure en France
from datetime import datetime


#Get the time now, local time FOR CLIENT SIDE (date from browser)
def french_zone_time():
    date_time = datetime.now(anvil.tz.tzlocal()) #recup browser time
    print(type(date_time))
    print(date_time)
    return date_time


# Calculate the difference beetween now time  and  't' (the str url time)
def time_over(t):
    bool=True #time is over

    #time now
    time_now=french_zone_time()
    #object creation from time url
    #   00000000011111111111
    #   01234567890123456789
    # t=2023-01-17_19:58:10.387213+01:00
    t=t.replace("_"," ")
    #alert(t)
    yy=int(t[0:4])
    mm=int(t[5:7])
    dd=int(t[8:10])
    hh=int(t[11:13])
    mi=int(t[14:16])
    ss=int(t[17:19])
    #print(f"{yy}-{mm}-{dd} {hh}-{mi}-{ss}")
    date_url=datetime(yy,mm,dd,hh,mi,ss,0, anvil.tz.tzlocal()) #construction of the url_time object
    # difference in minutes
    diff = (time_now - date_url)
    diff_in_minutes = diff.seconds/60

    # Lecture de la variable globale "timedelay_url_in_min" ds table variables_globales
    timedelay_url_in_min = anvil.server.call('get_variable_value', "timedelay_url_in_min")
    #to get the URL delay
    if diff_in_minutes < timedelay_url_in_min: # J
        bool = False # time not over
    return bool


# Returns the difference beetween now  and  a past date 
def time_diff(past_date):
    #time now
    time_now=french_zone_time()
    diff = time_now - past_date
    return diff