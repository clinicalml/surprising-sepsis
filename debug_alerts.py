import shelve
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

target = sys.argv[1]
s = shelve.open('patients/visitShelf')
current_time = None

alert_tracker = Alerter()
alerts = []
for e in sorted(expand(s[target]), key=sortkey):
    if 'COHORT-admission' in e['comment'][0]:
        print '\n\n'
        print '-'*20
        print e['comment'][0]

    if 'time' in e:
        if not e['time'][0] == current_time:
            current_time = e['time'][0]
    
    if 'COHORT-discharge' in e['comment'][0]:
        print e['comment'][0]
        print 'x'*20

    elif 'COHORT' in e['comment'][0]:
        print e
    
    alerts = alert_tracker.ingest(e)

    print e['time'][0],
    if 'LABS-recorded' in e['comment'][0]:
        print e['comment'][0], e['description'][0], e['result'][0], e['units'][0]
    elif 'VITALS-measured' in e['comment'][0]:
        print e['comment'][0], e['description'][0], e['result'][0]
    else:
        #print e['comment'][0], e
        pass
    if 'ALERT' in e['comment'][0]:
        print current_time, '\t', e['description'], alerts
        if len(alerts) < 2:
            print 'patient state:', alert_tracker.patient.get_combined_state()
            print 'csn', e['csn']
            print 'mrn', e['mrn']
