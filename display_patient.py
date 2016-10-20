import shelve
import cPickle as pickle
from Alerter import Alerter
import string
import datetime
import sys
from utils import sortkey



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

working_dir = sys.argv[1]
target = sys.argv[2]

patient_dir = working_dir+'/patients'

if 'vid' in sys.argv:
  csn_to_mrn = pickle.load(file(patient_dir+'/csn_to_mrn.pk'))
  target = csn_to_mrn[target]
s = shelve.open(patient_dir+'/visitShelf')
current_time = None


#alert_tracker = Alerter()
alerts = []
for e in sorted(expand(s[target]), key=sortkey):
    if 'time' in e:
        if not e['time'][0] == current_time:
            print e['time'][0],alerts
            current_time = e['time'][0]
    else:
        pass

    #alerts = alert_tracker.ingest(e)
    print e
    print '\t', e['comment'][0].strip(), 

    try:
        print ' '.join([z.strip() for z in e['description']]),'\t',
       
        if 'result' in e:
            print ' '.join([z.strip() for z in e['result']])
        else:
            print ''
    except:
        print e


