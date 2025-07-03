# -*- coding: utf-8 -*-
from file_management import download_file,open_file, delete_file # functions that download the lecture plan and delete it 
from data_management import data_analyse, sent_data #functions that analyse the data and send it to the database
import mysql.connector #MySQL database interaction
import time # Time-related functions.


def main():
    while(True):
    
        error = 0 # this variable is equal to 1 then the function after won't work and we will start everything from the beginning
        #connexion to the database
        conn = mysql.connector.connect(
            host="49.13.235.112",
            user="botEdtRemote",
            password="Dhbw@2024!",
            database="EDT"
        )
        #get the URL
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM url")
            tuple_url = cursor.fetchone()
            url = tuple_url[0]
        except Exception as e:
            error = 404  
            print(f"Error {error}. Problem related to the URL")

        #empty the database (change it later)
        try:
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE lessons;")
        except:
            print("Error with the database")
            error = 99            
        
    
        
        ##step 1 : download the lecture plan
        if error ==0:
            print("Code start")
            print(f"downloading the file from : {url}")    
            check, file_name = download_file(url) #the function return 1 if everything went as planned 0 if it doesn't and also return the name of the file that was downloaded
            if check == 0: 
                error = 1 #We change the value of error so the program won't go to the next step and do everything from the beginning 
                print(f"Error n°{error} while downloading")
            else:
                print("downloading done")    
        
        ##step 2 : open the file
        if error == 0:
            print("Opening the file")
            check, content = open_file(file_name)#return 1 if everything went well 0 if it doesn't. This function also return the content of the file.
            if check == 0:
                error = 2
                print(f"Error n°{error} while opening the file")
            else:
                print("opening done")

        
        ##step 3 : analyse the lecture plan
        if error == 0:
            print("Analysing the file")
            check, creation_date, last_modified, date_start, date_end, location, event_ID, summary, category, nb_element = data_analyse(content)#this function return 1 if everything went well and 0 otherwise.This function also return multiple list with all the important elements for every event 
            if check == 0:
                error = 3
                print(f"Error n°{error} while analysing the file")
            else:
                print("Analyse done")
                    
        ##step 4 : send the data to the database
        if error == 0:
            print("Sending the data")
            check = sent_data(conn, cursor,creation_date, last_modified, date_start, date_end, location,event_ID, summary, category, nb_element)#this programme return 1 if everything went well with sending the data
            if check == 0:
                error = 4
                print(f"Error n°{error} while sending the data to the database")    
            else:
                print("The data have been sent to the database successfully")

        ##step 5 : close the file and delete it 
        print("Deleting the file")
        check = delete_file(file_name)
        if check == 0:
            error = 5
            print(f"Error n°{error} while deleting/closing the file")
        else:
            print("The file has been succefully deleted")
        conn.close() 
        print("We wait for 5 mins before running the program again")
        time.sleep(300)#we wait 5 mins before running the program again
    
  

if __name__ == "__main__":
    main()