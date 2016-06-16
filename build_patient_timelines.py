import sys
import csv
import os
from fieldReader import FieldReader
from collections import defaultdict
import shelve

patient_records = defaultdict(list)

for datafile in os.listdir('data'):
    if 'sorted' in datafile:
        try:
          reader = FieldReader('data/'+datafile)
        except:
          continue
        print datafile
        for i,l in enumerate(reader):
            if not 'mrn' in l:
              print  'odd record', l,
            else:
              patient_records[l['mrn']].append(l)
            if (i+1)%10000 == 0:
                print i
                sys.stdout.flush()
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
