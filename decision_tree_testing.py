import cPickle as pickle
from fieldReader import FieldReader
from collections import defaultdict
import random
import datetime
import bisect
from multiprocessing import Pool
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm
import numpy as np
from generate_targets import *
from generate_vectors import *
from sklearn.metrics import roc_curve, precision_recall_curve



if __name__ == "__main__":

  working_dir = sys.argv[1]
  seed = 1028#np.random.randint(10000)
  np.random.seed(seed)
  random.seed(seed)
  print 'seed', seed

  deadlines = {}
  for l in file(working_dir+'/patients/times'):
    _vid = l.split()[0]
    t = ' '.join(l.split()[-2:])
    deadlines[_vid] = to_date(t)

  predictor = pickle.load(file(working_dir+'/output/classifier-pipeline.pk')) 

  def eval((X,Y)):
    times = [x[0] for x in X]
    X = np.vstack([x[1] for x in X])
    pred = predictor.predict_proba(X)
    max_pred = pred[:,1].max()
    y = Y[0]
    #max_predictions[t] holds the largest prediction seen up to time t
    max_predictions = {datetime.datetime.min:0}
    last_t=datetime.datetime.min
    for i,t in enumerate(sorted(times)):
      if pred[i,1] > max(max_predictions.values()):
        max_predictions[t] = pred[i,1]
    max_predictions.pop(datetime.datetime.min)
    return max_pred, y, max_predictions, times

  test_targets = generate_targets(test=True, directory=working_dir)
  random.shuffle(test_targets)
  vector_generator = VectorGenerator(N=None, working_dir=working_dir, debug=False)
  y_true = []
  y_score = []
  max_predictions = []
  times = []
  time_thresh = set()
  test_targets = test_targets

  vectors = vector_generator.generate(test_targets, processes=32)
  N = len(test_targets)
  #vectors = list(vectors)
  #print vectors[0], len(vectors[0][0])
  #sys.exit()
  pool = Pool(32)
  labels = {}
  prediction_cache = defaultdict(list)
  for i, (y_hat,y, max_pred, timestamps) in tqdm(enumerate(pool.imap(eval, vectors)), total=N):
    y_true.append(y)
    y_score.append(y_hat)
    max_predictions.append(max_pred)
    times.append(timestamps)
    vid = test_targets[i][2]
    labels[vid] = y
    for t, p in max_pred.items():
      prediction_cache[p].append((vid,t)) 
      time_thresh.add(p)
  

  fpr, tpr, thresh = roc_curve(y_true, y_score)
  prec, recall, thresh = precision_recall_curve(y_true, y_score)
  temp = [0]
  temp.extend(thresh)
  thresh=temp
  time_thresh = sorted(time_thresh)
  
  #plt.figure('ROC')
  #plt.title('ROC')
  #plt.plot(fpr, tpr)

  #plt.figure('PR curve')
  #plt.title('Precision Recall')
  #plt.plot(prec, recall)
  #plt.xlabel('recall')
  #plt.ylabel('precision')
  def quantiles(l):
    return [np.percentile(l, k) for k in (5,25,50,75,95)]


  #initialize the lead times vector
  lead_times = {}
  for i,(label,_,vid) in enumerate(test_targets):
    if label == -1:
      continue
    l = sorted(times[i])
    #print 'before min', vid, deadlines[vid], l[-1]
    if deadlines[vid].year == 9999:
      deadlines[vid] = l[-1]
    #print 'after min', vid, deadlines[vid], l[-1]
    deadline = deadlines[vid]
    alert_time = l[0]
    lead_times[vid] = (deadline - alert_time).total_seconds() / (60*60)



  lead_time_quantiles = []
  for t in time_thresh:
    closest_key = min(prediction_cache.keys(), key=lambda x: np.abs(x-t) + 1000*int(x>t))
    for vid,alert_time in prediction_cache[closest_key]:
      deadline = deadlines[vid]
      if labels[vid] == -1:
        continue
      lead_times[vid] = (deadline - alert_time).total_seconds() / (60.*60.)
    lead_time_quantiles.append(quantiles(lead_times.values()))

  reader = FieldReader('data/SEPSIS_ALERTS_2013-2014_2.DEID.csv', fields=working_dir+'/settings/FIELDS.txt')
  earliest_alert = defaultdict(lambda: datetime.datetime(datetime.MAXYEAR,1,1))
  for i, l in enumerate(reader):
    vid = str(l['csn'][0])
    earliest_alert[vid] = min(l['start'][0], earliest_alert[vid])
  predictions = []
  true_labels = []
  alert_leadtimes = []
  for _,_,vid in test_targets:
    predictions.append(int(earliest_alert[vid] < deadlines[vid]))
    true_labels.append(labels[vid])
    if true_labels[-1] == 1 and predictions[-1] == 1:
      alert_leadtimes.append((deadlines[vid] - earliest_alert[vid]).total_seconds() / (60.*60.))

  alert_prec, alert_recall, _ = precision_recall_curve(true_labels, predictions)
  print 'alert prec', alert_prec
  print 'alert recall', alert_recall

  n_pos = sum([y for y in y_true if y > 0])
  plt.figure('lead times')
  plt.subplot(3,1,3)
  plt.plot(thresh, prec, 'b')
  plt.plot([0,1], [alert_prec[1]]*2, 'r')
  plt.xlabel('threshold')
  plt.ylabel('precision')
  plt.subplot(3,1,2)
  plt.plot(thresh, [r*n_pos for r in recall], 'b')
  plt.plot([0,1], [alert_recall[1]*n_pos]*2, 'r')
  plt.ylabel('recall')
  plt.subplot(3,1,1)
  q5, q25, q50, q75, q95 = zip(*lead_time_quantiles)
  #plt.plot(time_thresh, q5, 'b-.')
  #plt.plot(time_thresh, q95, 'b-.')
  plt.plot(time_thresh, q25, 'b--')
  plt.plot(time_thresh, q75, 'b--')
  plt.plot(time_thresh, q50, 'b-')

  q5, q25, q50, q75, q95 = quantiles(alert_leadtimes)
  #plt.plot([0,1], [q5]*2, 'r-.')
  #plt.plot([0,1], [q95]*2, 'r-.')
  plt.plot([0,1], [q25]*2, 'r--')
  plt.plot([0,1], [q75]*2, 'r--')
  plt.plot([0,1], [q50]*2, 'r-')

  plt.xlim([0,1])
  plt.ylabel('lead-time (hrs)')
  plt.savefig(working_dir + '/output/precision_recall_leadtime.pdf')
  #plt.show()
