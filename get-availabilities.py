import csv
import json
import psycopg2
from credentials.secret_file import DB_DATABASE
from credentials.secret_file import DB_HOST
from credentials.secret_file import DB_PORT
from credentials.secret_file import DB_USER
from credentials.secret_file import DB_PASSWORD

if __name__ == "__main__":

    # Current induction class
    induction_class = "FA22"

    # Majors which map to specific departments for interview questions
    majors_map = {
        "Bioengineering": "BENG",
        "Cognitive Science - ML": "CSE",
        "Computer Engineering - CSE": "CSE",
        "Computer Science": "CSE",
        "CS - Bioinformatics": "CSE",
        "Data Science": "CSE",
        "EE and Society": "ECE",
        "Computer Engineering - ECE": "CSE",
        "Electrical Engineering": "ECE",
        "Engineering Physics": "ECE",
        "Aerospace Engineering": "MAE",
        "Mechanical Engineering": "MAE",
        "Math - Computer Science": "CSE",
        "Chemical Engineering": "MAE",
        "Nano Engineering": "MAE",
    }

    try:
        print("Attempting to connect to database...\n")
        # Connect to HKN production database (DO NOT SHARE CREDENTIALS)
        connection = psycopg2.connect(user=DB_USER,
                            password=DB_PASSWORD,
                            host=DB_HOST,
                            port=DB_PORT,
                            database=DB_DATABASE)
        cursor = connection.cursor()
        print("Database connected! Getting induction class", induction_class, "start interview date...")
        sql_get_start_interview_date = "SELECT \"interviewDates\" FROM induction_class WHERE quarter='" + induction_class + "'"
        cursor.execute(sql_get_start_interview_date)
        
        records = cursor.fetchone()

        #Parsing only the first 10 characters for the date to avoid timezone
        start_date = records[0][0][:10]
        print("We will only take in inductees and officers where their interview availabilities are after", start_date)

        officer_list = []
        inductee_list = []
        inductee_no_avails = []
        officer_no_avails = []
        
        numInductees = 0
        numOfficers = 0


        emails_list = []
        qualified_inductees_emails_path = 'inductee_emails.txt'
        current_officers_emails_path = 'officer_emails.txt'
        print("Opening", qualified_inductees_emails_path)
        with open(qualified_inductees_emails_path) as f:
            for line in f:
                line = line.strip()
                emails_list.append(line)
        print("Opening", current_officers_emails_path)
        with open(current_officers_emails_path) as f:
            for line in f:
                line = line.strip()
                emails_list.append(line)
        print("Looping through emails\n")

        sql_in_clause = "email IN ("
        for email in emails_list:
            sql_in_clause = sql_in_clause + "'" + email + "', "
        sql_in_clause = sql_in_clause[:len(sql_in_clause) - 2]
        sql_in_clause = sql_in_clause + ")"

        sql_get_inductees_and_officers = "SELECT * FROM app_user WHERE " + sql_in_clause
        cursor.execute(sql_get_inductees_and_officers)
        # get all records
        records = cursor.fetchall()
        for row in records:
            # We will do string comparisons to get the people who filled interview availabilities after a date
            if (row[8] is None or row[8][0]['start'] < start_date):
                print(row[1], row[2], "did not fill out their availabilities!")
                entry = {'name': row[1] + ' ' + row[2]}
                entry['email'] = row[3]
                if(row[6] == "inductee"):
                    inductee_no_avails.append(entry)
                else:
                    officer_no_avails.append(entry)   
                continue
            print("Id = ", row[0])
            print("firstName = ", row[1])
            print("lastName  = ", row[2])
            print("email = ", row[3])
            print("major = ", row[4])
            print("role = ", row[6])
            print("availabilities = ", row[8], "\n")

            # We will get rid of the time zone as a hotfix
            availabilities = row[8]

            # Timezone is after the 19 characters, so we will cut it out
            for availability in availabilities:
                availability['start'] = availability['start'][:19]
                availability['end'] = availability['end'][:19]

            entry = {'name': row[1] + " " + row[2]}
            entry['email'] = row[3]
            entry['major'] = majors_map[row[4]]
            entry['availability'] = [{
                'date': availabilities
            }]
            if(row[6] == "inductee"):
                numInductees = numInductees + 1
                inductee_list.append(entry)

            else:
                numOfficers = numOfficers + 1
                officer_list.append(entry)


    except psycopg2.Error as e:
        print("Error reading data from SQL table", e)
        if (connection):
            cursor.close()
            connection.close()
            print("Closed Database Connection")
        exit
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Closed Database Connection")

    print("Number of Officers:", numOfficers)
    print("Number of Inductees:", numInductees)
    result = {'officers': officer_list, 'inductees': inductee_list}

    with open('availability.json', 'w') as outfile:
        json.dump(result, outfile)

    print("Successfully filled availabilities for", induction_class, "quarter in availability.json")
    
    with open('unavailability_officer.csv', mode='w') as csv_file:
        fieldnames = ['officer', 'email']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for officer in officer_no_avails:
            writer.writerow({'officer': str(officer['name']), 'email': str(officer['email'])})
        if(len(officer_no_avails) != 0):
            print(len(officer_no_avails), "officer(s) have not submitted their availabilities! Check unavailability_officer.csv")
    
    with open('unavailability_inductee.csv', mode='w') as csv_file:
        fieldnames = ['inductee', 'email']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for inductee in inductee_no_avails:
            writer.writerow({'inductee': str(inductee['name']), 'email': str(inductee['email'])})
        if(len(inductee_no_avails) != 0):
            print(len(inductee_no_avails), "inductee(s) have not submitted their availabilities! Check unavailability_inductee.csv")