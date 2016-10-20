import shelve
import sys
from Patient import Patient
import cPickle as pickle
import numpy as np
from multiprocessing import Pool
from utils import to_date, expand, sortkey
import random
import itertools


directory = sys.argv[1]
output_dir = directory+'/output'
patients_dir = directory+'/patients'
print 'loading files'
try:
  vocab, inv_vocab = pickle.load(file(output_dir+'/vocab.pk'))
except:
  print 'warning, no vocab files!'
csn_to_mrn = pickle.load(file(patients_dir+'/csn_to_mrn.pk'))
ethnicities = pickle.load(file(patients_dir+'/ethnicities.pk'))
races = pickle.load(file(patients_dir+'/races.pk'))
demographics_offset = 4+len(ethnicities)+len(races)
deadlines = {}
for l in file(patients_dir+'/times'):
  _vid = l.split()[0]
  t = ' '.join(l.split()[-2:])
  deadlines[_vid] = to_date(t)
print 'done'



class VectorGenerator:
  def __init__(self, N=10, working_dir='.', debug=False):
    self.N = N
    self.working_dir = working_dir
    self.debug=debug

  def generate(self, targets, processes):
    if processes > 1:
      pool = Pool(processes)
      return pool.imap(generate_vectors, [(pid, vid, label, self.N, self.working_dir, self.debug) for (label, pid, vid) in targets])
    else:
      return itertools.imap(generate_vectors, [(pid, vid, label, self.N, self.working_dir, self.debug) for (label, pid, vid) in targets])
    
def generate_vectors((pid, vid, label, N, directory, debug), apply_filter=False):

  patient = Patient(pid, vid, inv_vocab)
  predictions = []
  offset = len(inv_vocab)
  patients_dir = directory+'/patients'
  s = shelve.open(patients_dir+'/visitShelf')
  d = shelve.open(patients_dir+'/demographics')

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
  demo_vec = np.hstack([demographics, patient.dense_feature_vector])
  #vec = patient.dense_feature_vector
  included_demographics = False
  for i, e in enumerate(sorted(events, key=sortkey)):
    t = e['time'][0]
    if debug:
      print t
    alerts, change = patient.update_state(e)
    if debug:
      print patient.temporal_state
    if 'future' in alerts or t >= break_point:
      break
    if patient.temporal_state == 'current' and change == True:
      if not included_demographics:
        vectors.append((t,demo_vec))  #demographics vector
        included_demographics = True
      vec = np.hstack([demographics, patient.dense_feature_vector])
      vectors.append((t,vec))
      
  if not included_demographics:
    vectors.append((t,demo_vec))  #demographics vector
    included_demographics = True

  if apply_filter == True:
    vectors = [max(vectors)] + filter(lambda v: (break_point - v[0]).total_seconds() < 60*60, vectors) #only keep vectors within an hour of physician notice
  if N is not None and len(vectors) > N:
    random.shuffle(vectors)
    vectors = vectors[:N]
  #print 'label', label
  return vectors, [label]*len(vectors)
