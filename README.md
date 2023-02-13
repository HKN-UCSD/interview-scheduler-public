# Interview Scheduler

To schedule interviews for HKN for every induction cycle...

- change `induction_class` in `get-availabilities.py` to be current induction class for interview schedules (ex: FA22)
- verify `majors_map` is correct and spans across all available majors in the database with associated bucketed interview questions
- fill `inductee_emails.txt` to be emails of inductees who qualified to be interviewed (should be given by induction branch of HKN)
- fill `officer_emails.txt` to be emails of current officers who are to interview candidates (should be given by induction branch of HKN)
- run `get-availabilities.py` in the same directory as the `inductee_emails.txt` file, which should generate a `availability.json` file
- run `schedule.py` in the same directory as the `availability.json` file, which should generate a `interview_schedule.csv` file and `unschedulable_inductees.csv` file



## get-availabilities.py
- connects to HKN's production database, queries appropriate officer and inductee availabilities (using only inductees from `inductee_emails.txt`), and creates a `availability.json` file which is to be used for `schedule.py` and a `unavailability.csv` if there are inductees who did not fill out their availabilities
- the script parses out relevant officers and inductees who filled out their availabilities for the induction cycle by...
    - getting `induction_class` start interview date from the database
    - getting all inductees in `inductee_emails.txt` and officers in `officer_emails.txt`
    - checks if availabilities of each fetched user are not null and are after `induction_class` start interview date (meaning availabilities are current)
    - maps majors to respective department for interviews through `majors_map`
    - writes to `availability.json`
- you can change `majors_map` to map majors with appropriate departments to bucket interview questions
- you can change `induction_class` for each induction cycle for interviews
- schema for availability.json looks like:
``` json
{
  "officers": [
    {
      "name": "Officer1 Officer1",
      "major": "Major",
      "availability": [
        {
          "date": [
            {
              "start": "ISO_timestring",
              "end": "ISO_timestring"
            }
          ]
        }
      ]
    },
    {
      "name": "Officer2 Officer2",
      "major": "Major",
      "availability": [
        {
          "date": [
            {
              "start": "ISO_timestring",
              "end": "ISO_timestring"
            }
          ]
        }
      ]
    }
  ],
  "inductees": [
    {
      "name": "Inductee1 Inductee1",
      "major": "Major",
      "availability": [
        {
          "date": [
            {
              "start": "ISO_timestring",
              "end": "ISO_timestring"
            }
          ]
        }
      ]
    },
    {
      "name": "Inductee2 Inductee2",
      "major": "Major",
      "availability": [
        {
          "date": [
            {
              "start": "ISO_timestring",
              "end": "ISO_timestring"
            }
          ]
        }
      ]
    }
  ]
}
```


    
    
## schedule.py
- takes the file `availability.json` and tries to schedule interviews based on it
- while it is within a fixed number of attempts, it attempts to greedy match the first availabilities matching inductee and 2 officers
    - at least one officer will have the same major as inductee
    - they all have to be available at one 1-hour time slot
    - starts matching from list of inductees, finding matching officers
- between every iteration it shuffles both lists
- after the trials, it picks the best scenario found, and outputs the final schedule into 2 csv
    - `interview_schedule.csv` contains columns `time, officer1, officer2, inductee` and has all the schedulable interviews that fit in the schedule 
    - `unschedulable_inductees.csv` contains inductees who could not be scheduled