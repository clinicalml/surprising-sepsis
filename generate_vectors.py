import shelve
from Patient import Patient
import cPickle as pickle
import numpy as np
from multiprocessing import Pool
from utils import to_date, expand, sortkey
import random
import itertools

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

class VectorGenerator:
  def __init__(self, N=10):
    self.N = N

  def generate(self, targets, processes):
    if processes > 1:
      pool = Pool(processes)
      return pool.imap(generate_vectors, [(pid, vid, label, self.N) for (label, pid, vid) in targets])
    else:
      return itertools.imap(generate_vectors, [(pid, vid, label, self.N) for (label, pid, vid) in targets])
    
def generate_vectors((pid, vid, label, N), apply_filter=False):
  s = shelve.open('patients/visitShelf')
  #d = shelve.open('patients/demographics')
  patient = Patient(pid, vid, inv_vocab)
  predictions = []
  offset = len(inv_vocab)

  #demographics = np.zeros((1,demographics_offset))
  #try:
  #  for entry in d[vid].split():
  #    k,val = entry.split(':')
  #    demographics[0,int(k)]=float(val)
  #except:
  #  print 'could not find demographics for', vid

  events = expand(s[str(pid)])
  #d.close()
  s.close()
  pred = 0
  break_point = deadlines[vid]
  vectors = []
  #vec = np.hstack([demographics, patient.dense_feature_vector])
  vec = patient.dense_feature_vector
  for i, e in enumerate(sorted(events, key=sortkey)):
    t = e['time'][0]
    if i == 0:
      vectors.append((t,vec))  #demographics vector
    alerts, change = patient.update_state(e)
    if 'future' in alerts or t >= break_point:
      break
    if patient.temporal_state == 'current' and change == True:
      #vec = np.hstack([demographics, patient.dense_feature_vector])
      vec = patient.dense_feature_vector
      vectors.append((t,vec))

  if apply_filter == True:
    vectors = [max(vectors)] + filter(lambda v: (break_point - v[0]).total_seconds() < 60*60, vectors) #only keep vectors within an hour of physician notice
  random.shuffle(vectors)
  if N is not None and len(vectors) > N:
    vectors = vectors[:N]
  return vectors, [label]*len(vectors)
