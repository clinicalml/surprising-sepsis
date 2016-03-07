#build_patient_vectors.py

from Patient import Patient
from multiprocessing import Pool
from collections import Counter, defaultdict
from utils import sortkey, invert_vocab, to_date, generate_targets, expand
from functools import partial
import cPickle as pickle
import datetime
import numpy as np
import random
import shelve
import string
import sys
import functools

csn_to_mrn = pickle.load(file('patients/csn_to_mrn.pk'))
ethnicities = pickle.load(file('patients/ethnicities.pk'))
races = pickle.load(file('patients/races.pk'))
demographics_offset = 1+3+len(ethnicities)+len(races)
print 'demographics_offset is', demographics_offset
random.seed(100)

# function that determines if the current record occurred after prediction deadline
def deadline_condition(self, record, deadline):
  #print record
  if 'start' in record and record['start'][0] and record['start'][0] >= deadline:
    return True
  else:
    return False

# build a list of patient vectors. One for every new observation.
def build_vector((label, pid, vid), train=True, break_at='discharge'):
  vectors = set()
  s = shelve.open('patients/visitShelf')
  d = shelve.open('patients/demographics')

  patient = Patient(pid, vid, inv_vocab, alert_conditions={'deadline':(partial(deadline_condition, deadline=deadlines[vid]),1)})

  for e in sorted(expand(s[pid]), key=sortkey):
    print e
    alerts = patient.update_state(e)
    print 'alerts', alerts
    if break_at in alerts:
      print 'break'
      break
    #svmlight format
    vectors.add(' '.join([str(label)]+[d[str(vid)]]+[str(a+demographics_offset)+':'+str(b) for a,b in patient.get_vector(inv_vocab)]+['#', pid, vid, break_at]))
  s.close()
  return vectors


test_targets = generate_targets(test=True)
train_targets = generate_targets(n_cases=None, n_controls=None)
override_vocab = 'override_vocab' in sys.argv
s = shelve.open('patients/visitShelf')
try:
  assert not override_vocab
  vocab, inv_vocab = pickle.load(file('output/vocab.pk'))
  print 'loaded vocabulary from output/vocab.pk' 
except:
  # building vocabulary
  key_counter = Counter()
  for label, pid, vid in train_targets:
    current_time = None
    patient = Patient(pid, vid, dry_run=True)
    print 'pid/vid', pid, vid
    for e in sorted(expand(s[pid]), key=sortkey):
      if(patient.update_state(e)):
        break
    for temporal_state in ['current']:
      key_counter.update(patient.get_combined_state().keys())

  vocab = sorted(key_counter.keys())
  inv_vocab = invert_vocab(vocab)
  pickle.dump((vocab, inv_vocab), file('output/vocab.pk', 'w'))


#read in patient prediction deadline for every patient and
#store in a dictionary
deadlines = {}
for l in file('patients/times'):
  vid = l.split()[0]
  t = ' '.join(l.split()[-2:])
  deadlines[vid] = to_date(t)
  
pool = Pool(1)

test_targets = generate_targets(test=True)
train_targets = generate_targets(n_cases=None, n_controls=None)

#break_at can be deadline or discharge
for break_at in ['deadline']:
  outfile = file('output/train_patient_vectors-'+break_at+'.svmlight', 'w')
  outfile = sys.stdout

  for i, vectors in enumerate(pool.imap(partial(build_vector, train=True, break_at=break_at), train_targets)):
    if i%100 == 0:
      print i

    for v in vectors:
      print >>outfile, v

  #outfile.close()

  #outfile = file('output/test_patient_vectors-'+break_at+'.svmlight', 'w')
  outfile = sys.stdout
  for i, vectors in enumerate(pool.imap(partial(build_vector, train=False, break_at=break_at), test_targets)):
    
    if i%100 == 0:
      print i

    for v in vectors:
      print >>outfile, v
  #outfile.close()
