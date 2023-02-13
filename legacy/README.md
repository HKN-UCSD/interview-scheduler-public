## generator.py (old unused file please ignore)
- takes a `names.txt` file, which contains a list of names separated by newlines
- in the script, you can change a couple of parameters for randomizing:
    - `random_seed` : seed for randomizing
    - `num_officers` : number of officers (interviewers)
    - `num_inductees` : number of people to interview
    - `start_hour` : earliest hour for interviews, in 24 hour time
    - `end_hour` : latest hour for interviews, in 24 hour time
    - `hour_lengths` : list of lengths by which to have people be randomly available for (every availability slot for someone will be of some element in `hour_lengths`)
    - `avail_prob_officer` : probability for an officer to be available on some time slot
    - `avail_prob_inductee` : probability for an inductee to be available on some time slot

- using these params, the script will take random names from the `names.txt` file you provide, and try to randomly generate availability slots based on the parameters above
- **By default, it will generate the availabilities in the current and next week of whenever you run the script, with every day having possible slots in between `start_hour` and `end_hour`**
-  When it is finished, it dumps the availbilities into a JSON `availability.json`
