import json
import csv
import random
import dateutil.parser
from datetime import datetime, timedelta

NUM_TRIALS = 10


class Person:
    def __init__(self, name, email, major, availability):
        self.name = name
        self.email = email
        self.major = major
        self.availability = availability

    def match(self, other):

        # for first interviewer(primary interviewer), major has to match
        if other.major != self.major:
            return None

        # find first matched interval
        for i1 in self.availability:
            for i2 in other.availability:
                if i1 == i2:
                    # remove interval from both people
                    self.removeInterval(i1)
                    other.removeInterval(i1)
                    return i1

        # return none if not found
        return None

    def removeInterval(self, interval):
        self.availability.remove(interval)

    def __str__(self):
        return self.name
    
    def __email__(self):
        return self.email


class Inductee(Person):
    def __init__(self, name, email, major, availability):
        super().__init__(name, email, major, availability)
        self.matched = 0  # matched interviewers
        self.matchedTime = None  # to store the time when one officer has matched
        self.interviewer1 = None
        self.interviewer2 = None


# misnomer: should be slot instead of interval, each interval is a non-divisible quantum
# of time
class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        if not isinstance(other, Interval):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.start == other.start and self.end == other.end

    def __str__(self):
        return "start: " + str(self.start) + " end: " + str(self.end)


class Interview:
    def __init__(self, interval, interviewer1, interviewer2, interviewee):
        self.interval = interval
        self.interviewer1 = interviewer1
        self.interviewer1_email = interviewer1.email
        self.interviewer2 = interviewer2
        self.interviewer2_email = interviewer2.email
        self.interviewee = interviewee
        self.interviewee_email = interviewee.email

    def __str__(self):
        return str(self.interval) + ":\t" + str(
            self.interviewer1).ljust(20) + str(
                self.interviewer2).ljust(20) + str(self.interviewee).ljust(20)


def parse_avail(availabilities):
    intervalList = []
    for a in availabilities:
        startTime = dateutil.parser.parse(a['start'])
        endTime = dateutil.parser.parse(a['end'])
        while startTime < endTime:
            intervalList.append(
                Interval(startTime, startTime + timedelta(hours=1)))
            startTime = startTime + timedelta(hours=1)
    return intervalList


with open('availability.json') as f:
    data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}

officerList = []
for o in data['officers']:
    availabilities = o['availability'][0]['date']
    officerList.append(
        Person(o['name'], o['email'], o['major'], parse_avail(availabilities)))

inducteeList = []
for o in data['inductees']:
    availabilities = o['availability'][0]['date']

    inducteeList.append(
        Inductee(o['name'], o['email'], o['major'], parse_avail(availabilities)))

print("Scheduling interviews for ", len(officerList), " officiers and ",
      len(inducteeList), " inductees...")

maxNumInterviews = 0
maxInterviewsScheduledInterviews = []
maxInterviewsUnscheduledInductees = []

for i in range(NUM_TRIALS):
    print("Trial: " + str(i + 1) + "\n", end="")

    # re-populate the two lists
    officerList = []
    inducteeList = []

    for o in data['officers']:
        availabilities = o['availability'][0]['date']
        officerList.append(
            Person(o['name'], o['email'], o['major'], parse_avail(availabilities)))

    for o in data['inductees']:
        availabilities = o['availability'][0]['date']
        inducteeList.append(
            Inductee(o['name'], o['email'], o['major'], parse_avail(availabilities)))

    random.shuffle(officerList)
    random.shuffle(inducteeList)

    scheduledInterviews = []
    unscheduledInductees = []

    count = 0  # used to break from the loop when we have rotated the entire officer list and cannot make more matches
    while len(inducteeList) != 0:

        if count == len(
                officerList
        ):  # have rotated entire officerList but cannot schedule interview for the first inductee in inducteeList
            count = 0
            unscheduledInductees.append(inducteeList[0])
            inducteeList.pop(0)
            continue

        currInductee = inducteeList[0]

        if currInductee.interviewer1 == officerList[0]:
            # already matched with current interviewer
            officerList = officerList[1:] + officerList[:1]
            count = count + 1
            continue

        if currInductee.matched == 1:  # already matched one

            # try to find the second interviewer at the same time slot
            if currInductee.matchedTime in officerList[0].availability:
                count = 0

                officerList[0].removeInterval(currInductee.matchedTime)
                # found the second interviewer
                currInductee.interviewer2 = officerList[0]
                # append to schedules
                scheduledInterviews.append(
                    Interview(interval, currInductee.interviewer1,
                              currInductee.interviewer2, currInductee))

                # remove inductee
                inducteeList.pop(0)
                officerList = officerList[1:] + officerList[:1]
                print("Matched", currInductee.name, "to", currInductee.interviewer2.name)
                continue
            else:
                officerList = officerList[1:] + officerList[:1]
                count = count + 1
                continue

        interval = officerList[0].match(currInductee)

        if interval is not None:
            count = 0

            currInductee.matched += 1
            currInductee.interviewer1 = officerList[0]
            currInductee.matchedTime = interval

            # rotate officer list, put the schdeduled officer in the end
            officerList = officerList[1:] + officerList[:1]
            print("Matched", currInductee.name, "to", currInductee.interviewer1.name)
        else:
            # if cannot schedule the first officer and the first inductee in the
            # list

            # if __debug__:
            #     print(str(officerList[0]) + "'s availabilities: ")
            #     for i in officerList[0].availability:
            #         print(str(i))

            #     print(str(inducteeList[0]) + "'s availabilities: ")
            #     for i in inducteeList[0].availability:
            #         print(str(i))
            #     print("failed to schedule\n")

            # rotate officer list, put the scheduled officer in the end
            officerList = officerList[1:] + officerList[:1]
            count = count + 1

    if (len(scheduledInterviews) > maxNumInterviews):
        maxNumInterviews = len(scheduledInterviews)
        maxInterviewsScheduledInterviews = scheduledInterviews
        maxInterviewsUnscheduledInductees = unscheduledInductees
    print("\n")

print("Succesfully scheduled " + str(maxNumInterviews) + " interviews. Check interview_schedule.csv for schedule.\n")

with open('interview_schedule.csv', mode='w') as csv_file:
    fieldnames = ['time', 'officer1', 'officer2', 'inductee', 'interview_type']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for s in maxInterviewsScheduledInterviews:
        writer.writerow({
            'time': str(s.interval),
            'inductee': str(s.interviewee) + " (" + str(s.interviewee_email) + ")",
            'officer1': str(s.interviewer1) + " (" + str(s.interviewer1_email) + ")",
            'officer2': str(s.interviewer2) + " (" + str(s.interviewer2_email) + ")",
            'interview_type': str(s.interviewee.major)
        })

with open('unschedulable_inductees.csv', mode='w') as csv_file:
    fieldnames = ['inductee', 'email']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for s in maxInterviewsUnscheduledInductees:
        writer.writerow({'inductee': str(s), 'email': s.email})
    if(len(maxInterviewsUnscheduledInductees) == 0):
        print("All inductees successfully scheduled!\n")
    else:
        print("Unable to schedule", len(maxInterviewsUnscheduledInductees), "interview(s). Please check unschedulable_inductees.csv.")
        print("You can run schedule.py again with more NUM_TRIALS to see if you get better results.\n")
