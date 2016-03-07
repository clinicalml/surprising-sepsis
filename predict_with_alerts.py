import sys
from collections import defaultdict
import datetime
import shelve
import string
import cPickle as pickle
from fieldReader import FieldReader
from utils import sortkey, to_date
import csv

deadlines = {}
for l in file('patients/times'):
  vid = l.split()[0]
  t = ' '.join(l.split()[-2:])
  deadlines[vid] = to_date(t)

def extract_from(record, inclusion):
    return (r for r in record if r['comment'][0].lower() in inclusion)

csn_to_mrn = pickle.load(file('patients/csn_to_mrn.pk'))
test_csn = [int(l.split()[0]) for l in file('patients/test_sepsis_labels.txt').readlines()]
reader = FieldReader('data/SEPSIS_ALERTS_2013-2014_2.DEID.csv')
earliest_alert = defaultdict(lambda: datetime.datetime(datetime.MAXYEAR,1,1))
for i, l in enumerate(reader):
    if i % 100000 == 0:
      print i

    #pid = l['mrn'][0]
    vid = str(l['csn'][0])
    earliest_alert[vid] = min(l['start'][0], earliest_alert[vid])

outfile = file('output/alert_predictions-deadline.txt', 'w')
for vid in test_csn:
  #pid = int(csn_to_mrn[str(vid)])
  if earliest_alert[str(vid)] < deadlines[str(vid)]:
      print >>outfile, vid, 1, (earliest_alert[str(vid)] - deadlines[str(vid)]).total_seconds()
  else:
      print >>outfile, vid, 0, "None"
outfile.close()
