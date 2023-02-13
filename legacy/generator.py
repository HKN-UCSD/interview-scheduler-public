import random
import datetime
import json


def make_times(start_hour, end_hour, hour_lengths, avail_prob):
    result = []
    dt = datetime.date.today()
    start_date = dt - datetime.timedelta(days=dt.weekday() + 1)
    end_date = start_date + datetime.timedelta(days=6)
    days = []
    while start_date <= end_date:
        days.append(start_date)
        start_date += datetime.timedelta(days=1)

    start_time = datetime.time(hour=start_hour)
    end_time = datetime.time(hour=end_hour)

    time_diffs = []
    for h in hour_lengths:
        time_diffs.append(datetime.timedelta(hours=h))

    for d in days:
        start = datetime.datetime.combine(d, start_time)
        end = datetime.datetime.combine(d, end_time)
        while start < end:
            step = random.choice(time_diffs)
            end_sec = start + step
            if (end_sec > end):
                end_sec = end

            if random.random() < avail_prob:
                result.append({
                    'start': start.isoformat(),
                    'end': end_sec.isoformat()
                })

            start = end_sec

    return result


def make_availability(names, start_hour, end_hour, prob):
    entry_list = []
    for n in names:
        entry = {'name': n}
        entry['major'] = random.choice(majors_list)
        entry['availability'] = [{
            'date':
            make_times(start_hour, end_hour, hour_lengths, prob)
        }]
        entry_list.append(entry)
    return entry_list


if __name__ == "__main__":
    majors_list = [
        'ECE', 'CSE', 'BENG', 'MAE', 'DSC', 'MATH-CS', 'COGS-ML', 'NANO-EE'
    ]

    names_path = 'names.txt'

    names_list = []
    with open(names_path) as f:
        for line in f:
            line = line.strip()
            names_list.append(line)

    random_seed = 0

    # set params for number of ppl
    num_officers = 10
    num_inductees = 50
    random.seed(random_seed)

    # get names for officers and inductees
    temp = random.sample(names_list, num_officers + num_inductees)
    officers = temp[:num_officers]
    inductees = temp[num_officers:]

    # set params for randomization
    start_hour = 10
    end_hour = 18
    hour_lengths = [1, 2, 4]
    avail_prob_inductee = 0.1
    avail_prob_officer = 0.5

    # make availabilities
    off = make_availability(officers, start_hour, end_hour, avail_prob_officer)
    ind = make_availability(inductees, start_hour, end_hour, avail_prob_inductee)
    result = {'officers': off, 'inductees': ind}

    with open('availability.json', 'w') as outfile:
        json.dump(result, outfile)
