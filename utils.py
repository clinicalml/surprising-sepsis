import datetime
from Patient import Patient
import shelve
import numpy as np
import cPickle as pickle
import random



#utility to change date strings that appear in the records
#to python datetime objects
def to_date(d):
  try:
    return datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
  except:
    return datetime.datetime.strptime(d, "%Y/%m/%d %H:%M:%S")

try:
  vocab, inv_vocab = pickle.load(file('output/vocab.pk'))
except:
  print 'warning, no vocab files!'
csn_to_mrn = pickle.load(file('patients/csn_to_mrn.pk'))
ethnicities = pickle.load(file('patients/ethnicities.pk'))
races = pickle.load(file('patients/races.pk'))
demographics_offset = 4+len(ethnicities)+len(races)
deadlines = {}
for l in file('patients/times'):
  vid = l.split()[0]
  t = ' '.join(l.split()[-2:])
  deadlines[vid] = to_date(t)


#sort primarily by date
#secondary sorting so that alerts go after the data that
#that triggered them is present.
def sortkey(e):
    if 'time' in e and not None in e['time']:
        return (e['time'][0], 'ALERTS' in e['comment'][0])
    else:
        return (datetime.datetime(datetime.MINYEAR,1,1), True)

#util to build an inverse vocab that maps words to indices.
def invert_vocab(v):
    return dict(zip(v, xrange(len(v))))


#expand records. If multiple timestamps exist for a single 
#record (e.g., sample ordered, sample taken, value recorded),
#break into multiple records.
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

#create a random set of patient ids with a set number of
#positive labels (cases), negative labels (controls), alerts.
#if test is true, use all of the test patients.
def generate_targets(n_cases=0, n_controls=0, n_alerts=0, test=False):
  csn_to_mrn = pickle.load(file('patients/csn_to_mrn.pk'))
  alert_csns = set()
  case_csns = set()
  control_csns = set()

  if test:
    label_file = 'patients/test_sepsis_labels.txt'
  else:
    label_file = 'patients/train_sepsis_labels.txt'
    for l in file('output/alert_predictions.txt'):
      csn = l.split()[0]
      label = l.split()[1]
      if label == '1':
        alert_csns.add(csn)

  for l in file(label_file):
    csn = l.split()[0]
    label = l.split()[1]
    if label == '1':
      case_csns.add(csn)
    else:
      control_csns.add(csn)

  targets = []
  labels = [None, -1, 1]
  for group,label,N in ((alert_csns, None, n_alerts), (case_csns,1, n_cases), (control_csns,-1,n_controls)):
    group = list(group)
    random.shuffle(group)
    if test:
      targets.extend([(label, csn_to_mrn[vid],vid) for vid in group])
    else:
      targets.extend([(label, csn_to_mrn[vid],vid) for vid in group[:N]])
  return targets


def generate_vectors((pid, vid, label, N), apply_filter=False):
  s = shelve.open('patients/visitShelf')
  d = shelve.open('patients/demographics')
  patient = Patient(pid, vid, inv_vocab)
  predictions = []
  offset = len(inv_vocab)

  demographics = np.zeros((1,demographics_offset))
  try:
    for entry in d[vid].split():
      k,val = entry.split(':')
      demographics[0,int(k)]=float(val)
  except:
    print 'could not find demographics for', vid

  events = expand(s[str(pid)])
  d.close()
  s.close()
  pred = 0
  break_point = deadlines[vid]
  vectors = []
  vec = np.hstack([demographics, patient.dense_feature_vector])
  for i, e in enumerate(sorted(events, key=sortkey)):
    t = e['time'][0]
    if i == 0:
      vectors.append((t,vec))  #demographics vector
    alerts, change = patient.update_state(e)
    if 'future' in alerts or t >= break_point:
      break
    if patient.temporal_state == 'current' and change == True:
      vec = np.hstack([demographics, patient.dense_feature_vector])
      vectors.append((t,vec))

  if apply_filter == True:
    vectors = [max(vectors)] + filter(lambda v: (break_point - v[0]).total_seconds() < 60*60, vectors) #only keep vectors within an hour of physician notice
  random.shuffle(vectors)
  if len(vectors) > N:
    vectors = vectors[:N]
  #for t,v in vectors:
  #  print v[0][:10]
  return vectors, [label]*len(vectors)
