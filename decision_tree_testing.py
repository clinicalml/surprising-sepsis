import cPickle as pickle
from functools import partial
from multiprocessing import Pool
import random
import sys
import scipy.sparse as sparse
import shelve
import numpy as np
from Patient import Patient
from utils import expand, sortkey, to_date, generate_vectors#, generate_targets

vocab, inv_vocab = pickle.load(file('output/vocab.pk'))
csn_to_mrn = pickle.load(file('patients/csn_to_mrn.pk'))
ethnicities = pickle.load(file('patients/ethnicities.pk'))
races = pickle.load(file('patients/races.pk'))
demographics_offset = 3+len(ethnicities)+len(races)
random.seed(100)

deadlines = {}
for l in file('patients/times'):
  vid = l.split()[0]
  t = ' '.join(l.split()[-2:])
  deadlines[vid] = to_date(t)


def generate_targets(n_cases=0, n_controls=0, n_alerts=0, test=False):
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

def evaluate_predictor((label, pid, vid, vectors), predictor, threshold, mask):
  predictions = []
  alert_time = None
  #print vectors
  vec_mat = []
  for vec, _ in zip(*vectors):
    t,vec = vec
    vec_mat.append(vec[0])
  vec_mat = np.vstack(vec_mat)[:, mask]
  predictions = predictor.predict_proba(vec_mat)[:, 1]

  return label, pid, vid, max(predictions), alert_time

if __name__ == "__main__":
  mask, predictor = pickle.load(file(sys.argv[1])) 
  try:
    threshold = float(sys.argv[2])
  except:
    threshold = None

  pool = Pool(48)
  #predictor.best_estimator_.set_params(n_jobs=1)
  test_targets = generate_targets(test=True)

  evaluate = partial(evaluate_predictor, predictor=predictor, threshold=threshold, mask=mask)

  outfile = file('output/decision_tree_predictions-deadline.txt', 'w')
  
  #for i, target in enumerate(test_targets):
  #  label, pid,vid,pred,alert_time = evaluate(target)
  #vectors = []
  #for l,p,v in test_targets:
  #  vectors.append(generate_vectors((p,v,l,float('inf'))))

  print 'generating vectors'
  vectors = pool.map(generate_vectors, ((p,v,l,float('inf')) for l,p,v in test_targets))
  test_targets_vec = [(l, p, v, vec) for (l,p,v),vec in zip(test_targets, vectors)]
  print 'done'

  print 'evaluating vectors'
  for i, (label, pid, vid, pred, alert_time) in enumerate(pool.imap(evaluate, test_targets_vec, chunksize=30)):
    if i% 1000 == 0:
      print i
    if alert_time is None:
      print >>outfile, vid, pred, None
    else:
      print >>outfile, vid, pred, (alert_time - deadlines[vid]).total_seconds()
  outfile.close()
