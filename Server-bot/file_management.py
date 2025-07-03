# -*- coding: utf-8 -*-
import os #File and operating system operations
import requests #Makes HTTP requests.

#this function is responsible of the downloading part
def download_file(url):
    try : # to avoid the fact that the program will stop if there is a mistake we do a "try" and if there is an error in that part then we'll go in the except part
        print("download start...")
        response = requests.get(url) #this command is used to download
        response.raise_for_status()#here to check that everything went well
        file_name = "Alle_Raume.ics"#rélgler le pb du nom du fichier 
        with open(file_name, "wb") as f:#this part allows us to save the file
            f.write(response.content)
        path = os.path.abspath(file_name)
        print(f"The file is saved here : {path}")
        check = 1 #everything went well so check = 1 it is going to be used in the main program
    except requests.exceptions.RequestException as e:#if there is a problem in the "try" then we will do this part 
        check = 0 #if there is a problem then check = 0 this is going to be used in the main program
        file_name = " " 
    return check, file_name

#this function will be responsible of the opening part of the file 
def open_file(file_name):
    try: # the programm will try to do this part 
        with open(file_name, "r", encoding="utf-8") as file: #we open the file and we read it (that is what mean the "r")
            content = file.read() #the variable "content" will take for value the content of the file 
        check = 1#since everything went well check = 1
    except FileNotFoundError: #if we don't find the file then
        content = " " # the variable content is empty
        check = 0 # the program is not working so check = 0
    except Exception as e: #if there is another exception in the "try"
        content = " " #then the content is empty 
        check = 0 #and check = 0 because the program did not work
    return check, content

#this function is responsible of deleting the file so we do not use a lot of memory
def delete_file(file_name):
        try: #the program will try to delete the file 
            os.remove(file_name) #this line delete the file
            check = 1 #since everything went well then check = 1
        except Exception : #if there is any problem in the "try" then the program do no work 
            check = 0 # since the program do not work 
        return check



