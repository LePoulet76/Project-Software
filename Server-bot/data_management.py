# -*- coding: utf-8 -*-
import re #used for pattern matching in strings — like extracting dates, times, or cleaning data
import convert_time
from datetime import datetime, timedelta # datetime: to represent and manipulate dates and times timedelta: to do time arithmetic (e.g., adding 30 minutes).
import pytz#Time zone handling.
def unfold_lines(content):
    # Combine folded lines: lines that start with space/tab continue the previous one
    return re.sub(r'[\r\n]+[ \t]', '', content)

def data_analyse(content):
    creation_date = [] # this list will contain all the date of creation of every event 
    last_modified = [] # this list will contain all the date of last modification of every event 
    date_start = [] # this list will contain all the date when the every event start 
    date_end = [] # this list will contain all the date when the event end for every event
    location = [] # this list will contain all the location of every event
    event_ID = [] # this list will contain all the ID of every event
    summary = [] # this list will contain all the summary of every event
    categories = [] # this list will contain all the categories of every event

    try:
        nb_element = 0 #this variable will allow us to count the number of element in every list
        index = 0 #this variable tracks the current line number in the content
        end_of_setup = 0 #this variable will be set to 1 once we reach the relevent part of the code (after the end of the setup of the calendar)
        lines = unfold_lines(content).splitlines()#this line allows us to take all the content and put it in a list where every element is a line of the content
        check = 1 #initially "check" should be set at 1 and will only be change id there is a problem in the code
        while index < len(lines):#as long as we are not at the end of the content (so as long as the index is smaller or as the same value than the number of line in the content)
            if lines[index] != "BEGIN:VEVENT":#as long as we are still in the setup part of the calendar we continue reading the content and add 1 to the index  
                index += 1
                continue
            else:#once we see this "tag" then it means that we are at the beginning of the creation of one event in the calendar. This also means that we are done with the setup phase so we can start looking at the data and informations we have 
                index+=1
                end_of_setup = 1 #end of the setup phase of the calender
            if end_of_setup == 1:# if the setup phase is done then we can do the folowwing part of the code that "tri" all the data in different list
                while index < len(lines) and lines[index] != "END:VEVENT":#as long as we are not at the end of the event declaration, then we need to store every data in the appropriate list
                    elements = lines[index].split(":",1)#this will create the list of elements from the line, split at the occurence of ":"
                    if len(elements) != 2:
                        print(f"Ligne mal formatée à index {index} : {lines[index]}")
                    #by looking at the first part of the line we can determine the type of information that follows and store it in the appropriate list
                    if elements[0] == "BEGIN" or elements[0] == "LAST-MODIFIED":
                        pass #there is no relevent information about the event
                    elif elements[0]=="DTSTAMP":
                        date_modified = convert_time.convert_datetime(elements[1])
                        last_modified.append(date_modified)
                    elif elements[0]=="CREATED":
                        date_created = convert_time.convert_datetime(elements[1])
                        creation_date.append(date_created)
                    elif elements[0]=="DTSTART" or elements[0]=="DTSTART;TZID=Europe/Berlin":
                        start_date =  convert_time.convert_datetime(elements[1])
                        date_start.append(start_date)
                    elif elements[0]=="DTEND" or elements[0] == "DTEND;TZID=Europe/Berlin":
                        end_date = convert_time.convert_datetime(elements[1])
                        date_end.append(end_date)
                    elif elements[0]=="UID":
                        event_ID.append(elements[1])
                    elif elements[0]=="SUMMARY":
                        summary.append(elements[1])
                    elif elements[0]=="LOCATION":
                        location.append(elements[1])
                    elif elements[0]=="CATEGORIES":
                        categories.append(elements[1])
                    else:#there is an information that is not important for us 
                        pass
                    
                    index+=1 #we go to the next line 
                
                nb_element += 1 # We have finished storing all the information about the event, so we can say that one element has been fully processed
            index+=1
        #print(f"check = {check}")
    except IndexError: #if the index is out of range then it means there is a problem
        print("Index error")
        check = 0
    except ValueError: #if the value is not correct due to an issue with the splitting operation
        print("Wrong value")
        check = 0
    except Exception as e: #if there is anything unexpected
        print(f"Unexpected error {e}")
        check = 0
    return check, creation_date, last_modified, date_start, date_end, location, event_ID, summary, categories, nb_element

def sent_data(conn, cursor,creation_date, last_modified, date_start, date_end, location, event_ID, summary, categories, nb_element):
    try:
        timezone = pytz.timezone('Europe/Paris')#we define the timezone
        now = datetime.now(timezone)#we define the time of today
        yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        number_of_event = 0
        number_of_event_not_saved = 0
        for i in range(nb_element): #we will insert the values into the database using the following SQL command
            if date_start[i]>=yesterday:#to make sure it will not take to much time we only send the event that are from yesterday to the end of the lecture plan
                insert_values = "INSERT INTO lessons (creationDate, modificationDate, startDate, endDate, location, ID, summary, category) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (creation_date[i],last_modified[i],date_start[i],date_end[i],location[i],event_ID[i],summary[i],categories[i])
                cursor.execute(insert_values,tuple(values))
                number_of_event += 1
                if number_of_event % 100 == 0:#we send the information to the database 100 by 100
                    conn.commit()
            else:
                number_of_event_not_saved +=1
        conn.commit()
        check = 1
        print(f"We didn't upload {number_of_event_not_saved} events because they were before the date : {yesterday}")
    except Exception as e:
        print(f"Error : {e}")    
        check = 0
    return check