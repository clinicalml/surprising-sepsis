import datetime
from fieldReader import FieldReader
from collections import defaultdict

reader = FieldReader('data/SEPSIS_COHORT_2013-2014_2.DEID.csv')

units = defaultdict(int)
for i,l in enumerate(reader):
    units[l['unit']] += 1

for u in sorted(units.items(), key=lambda u: u[1]):
    print u

