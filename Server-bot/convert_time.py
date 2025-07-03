# -*- coding: utf-8 -*-
from datetime import datetime #to represent and manipulate dates and times.
import pytz #Time zone handling.

def convert_datetime(date_str):
   # this function take a time in ISO format (ex: '2024-06-01T15:00:00Z') and return the time in GTM+1 or UTC+2 (depending if we use the winter time or the standard time) in a format that can be understant by the database (YYYY-mm-dd HH:MM:SS)
    try:
    # Conversion from str to datetime
        if date_str.endswith("Z"):
            utc_time = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ") #convert into an object 
            utc_zone = pytz.utc # it give us the time zone
            utc_time = utc_zone.localize(utc_time) #the time is now in GTM+0 

            # convert in timezone Europe/Paris which is the same as in Germany
            paris_zone = pytz.timezone('Europe/Paris')
            local_time = utc_time.astimezone(paris_zone)
            return local_time#.strftime('%Y-%m-%d %H:%M:%S')#this return the date and time in a format that the database will understand
        else:
            local_time = datetime.strptime(date_str, "%Y%m%dT%H%M%S")
            paris_zone = pytz.timezone('Europe/Paris')
            local_time = paris_zone.localize(local_time)
            return local_time#.strftime('%Y-%m-%d %H:%M:%S')#this return the date and time in a format that the database will understand
    except Exception as e:
        print(f"Error convert time : {e}")
        return None