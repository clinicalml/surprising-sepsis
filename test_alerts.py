import sys
from multiprocessing import Pool
import shelve
import cPickle as pickle
import numpy as np
from Alerter import Alerter
import string
import datetime
from utils import sortkey
import random

csn_to_mrn = pickle.load(file('patients/csn_to_mrn.pk'))
random.seed(100)

def generate_targets(filename, N):
    alert_csns = set()
    for l in file(filename):
        csn = l.split()[0]
        label = l.split()[1]
        if label == '1':
            alert_csns.add(csn)

    alert_csns = list(alert_csns)
    random.shuffle(alert_csns)
    return [(csn_to_mrn[vid],vid) for vid in alert_csns[:N]]
        
def expand(records):
    l = []
    for r in records:
        for k,val in r.items():
            if type(val[0]) == datetime.datetime:
                entry = dict(r)
                entry['comment']= (entry['comment'][0]+'-'+k,)
                entry['time'] = val
                l.append(entry)
    return l

def directly_generate_targets(N):
  for l in file('test_alerts.out'):
    pid, vid = l.split(',')[0].split()[1], l.split(',')[1]
    if '[' in l:
      raise StopIteration
    yield pid, vid


  

if len(sys.argv) > 1:
  vid = sys.argv[1]
  targets = [(csn_to_mrn[vid], vid)]
  verbose = True
else:
  #targets = generate_targets('output/alert_predictions.txt', 1000)
  targets = directly_generate_targets(1000)
  verbose = False

def check_alert((pid,vid)):
    s = shelve.open('patients/visitShelf-update')
    current_time = None
    alert_tracker = Alerter()
    alerts = []
    if  verbose:
      for e in sorted(expand(s[pid]), key=sortkey):
        if 'start' in e:
          print e['start'][0], e
        else:
          print e['time'][0], e

    for e in sorted(expand(s[pid]), key=sortkey):
        alerts = [a for a,_ in alert_tracker.ingest(e)]
        if 'ALERT' in e['comment'][0] and int(vid) in e['csn']:
            if len(alerts) >= 2 or 'bp' in alerts or 'lactate' in alerts:
                print 'good', ','.join(map(str, [pid,vid,e['start'][0], e['description'][0], ';'.join(alerts)]))
                return 1
            else:
                print 'bad', ','.join(map(str, [pid,vid,e['start'][0], e['description'][0], ';'.join(alerts)]))
                return 0
            break

pass_fail = [0,0]
pool = Pool(48)
retval = pool.imap(check_alert, targets)
for i, r in enumerate(retval):
  sys.stdout.flush()
  pass_fail[r] += 1

print '0/1', pass_fail
