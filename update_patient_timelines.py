import sys
import csv
import os
from fieldReader import FieldReader
from collections import defaultdict
import shelve

working_dir = sys.argv[1]
files_to_read = sys.argv[2:]

patient_records = defaultdict(list)
for datafile in files_to_read:
    reader = FieldReader('data/'+datafile.strip(), fields=working_dir+'/settings/FIELDS.txt')
    for i,l in enumerate(reader):
        if not 'mrn' in l:
          print  'odd record', l,
        else:
          patient_records[l['mrn']].append(l)
        if (i+1)%10000 == 0:
            print i
            print l
            sys.stdout.flush()
    print 'done'
    sys.stdout.flush()

print 'writing shelf'
sys.stdout.flush()
s = shelve.open(working_dir+'/patients/visitShelf', 'c')
for i, (k,val) in enumerate(patient_records.iteritems()):
    if i % 100 == 0:
        print 'patient', i,'/',len(patient_records)
        sys.stdout.flush()
    my_val = s[str(k[0])]
    #remove all problem list items from the original list
    my_val = [x for x in my_val if 'csn' in x]

    #add back into the original database
    my_val.extend(val)
    s[str(k[0])] = my_val
s.close()
