import sys
import csv
import os
from fieldReader import FieldReader
from collections import defaultdict
import shelve

patient_records = defaultdict(list)

for datafile in os.listdir('data'):
    if 'sorted' in datafile:
        reader = FieldReader('data/'+datafile)
        sys.stdout.flush()
        for i,l in enumerate(reader):
            patient_records[l['mrn']].append(l)
            if i%1000 == 0:
                print i
    print 'done'
    sys.stdout.flush()

print 'writing shelf'
sys.stdout.flush()
s = shelve.open('patients/visitShelf', 'n')

for i, (k,val) in enumerate(patient_records.iteritems()):

    if i % 100 == 0:
        print 'patient', i,'/',len(patient_records)
        sys.stdout.flush()
    s[str(k[0])] = val

s.close()
