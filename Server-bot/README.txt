Lecture Plan Bot - README
---------------------------

This program is a bot designed to automatically fetch, process, and store data from a university lecture calendar (.ics file) into a MySQL database.

--------------------------------------------------------------
🔧 Dependencies

To run this program, install the required Python packages:

    pip install mysql-connector-python pytz requests

--------------------------------------------------------------
📌 What the Bot Does

1. Retrieves the calendar URL from the database.
2. Clears the "lessons" table where event data is stored.
3. Downloads the .ics lecture plan file from the provided URL.
4. Parses and extracts relevant event information.
5. Inserts the relevant data into the database.
6. Deletes the file locally to save space.

All steps are completed approximately every 5 minutes.

--------------------------------------------------------------
🗂️ File Structure

The project is organized into four modules:

- **Main Program**: Connects to the database, retrieves the calendar URL, and coordinates all function calls.
- **File Management Module**: Handles downloading, opening, and deleting the .ics file.
- **Data Management Module**: Extracts and prepares event data from the .ics file and sends it to the database.
- **Time Conversion Module**: Contains a helper function to convert .ics timestamps to MySQL datetime format.

--------------------------------------------------------------
🧠 Example of a Calendar Event (ICS format)

Each event in "Alle_Raume.ics" looks like:

    BEGIN:VEVENT
    LAST-MODIFIED:20250408T101243Z
    CREATED:20250408T101212Z
    DTSTART:20250417T080000Z
    DTEND:20250417T100000Z
    UID:a4d1bded-d412-4ab7-8978-bb1fbbcc2e08
    SUMMARY:IT.S - Bewerbungsgespräch
    LOCATION:H108b\, Besprechungsraum
    CATEGORIES:Sonstiger Termin
    END:VEVENT

Extracted fields:
- CREATED (Creation date)
- LAST-MODIFIED
- DTSTART (Start date/time)
- DTEND (End date/time)
- UID (Event ID)
- SUMMARY (Title)
- LOCATION
- CATEGORIES

Parsing stops at the line: `END:VCALENDAR`

--------------------------------------------------------------
📂 Module & Function Overview

🔸 File Management Module (imports: `os`, `sys`, `datetime`, `requests`)
- `download_file(url)`  
  Downloads the .ics file and saves it as `Alle_Raume.ics`.  
  Returns: `check` (1=success, 0=fail), and file name.

- `open_file(file_name)`  
  Opens and reads the file content.  
  Returns: `check`, `content`.

- `delete_file(file_name)`  
  Deletes the local file.  
  Returns: `check`.

🔸 Data Management Module (imports: `re`, `convert_time`, `datetime`, `pytz`)
- `unfold_lines(content)`  
  Reconstructs folded lines in the .ics file (those starting with a space/tab).

- `data_analyse(content)`  
  Parses the content, stores event fields into separate lists.  
  Returns: `check`, and lists for each field (creation, last-modified, start, end, etc.), plus event count.

- `sent_data(...)`  
  Filters out outdated events and sends relevant ones to the database.  
  Returns: `check`.

🔸 Time Conversion Module (imports: `datetime`, `pytz`)
- `convert_datetime(timestamp)`  
  Converts .ics timestamp to MySQL datetime format (`YYYY-MM-DD HH:MM:SS`).

--------------------------------------------------------------
🕒 Runtime

The program runs in an infinite loop and re-executes every 5 minutes using `time.sleep(300)`.

--------------------------------------------------------------
Server configuration part :

/configuration_server : the file bot_launch.service is the file inside the server that allow (with enable daemons) to launch the bot at the start of the server and restart in cas of crash.
