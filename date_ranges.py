import datetime
from fieldReader import FieldReader
from collections import defaultdict

reader = FieldReader('data/SEPSIS_COHORT_2013-2014_2.DEID.csv')

earliest = defaultdict(lambda: datetime.datetime(datetime.MAXYEAR, 1,1))
latest = defaultdict(lambda: datetime.datetime(datetime.MINYEAR, 1,1))
difference = {}
for i,l in enumerate(reader):
    csn = l['mrn']
    admission = l['admission'][0]
    if admission == None:
        continue

    discharge = l['discharge'][0]
    if discharge == None:
        continue

    if admission < earliest[csn]:
        earliest[csn] = admission
        difference[csn] = latest[csn] - earliest[csn]
    if discharge > latest[csn]:
        latest[csn] = discharge
        difference[csn] = latest[csn] - earliest[csn]

print max(difference.values())

