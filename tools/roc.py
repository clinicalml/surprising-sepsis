import sys
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve
import string
import numpy as np
import datetime


labels = {'b':'decision tree', 'r':'2/6 SIRS'}
colors = 'brg'
name = sys.argv[1]
for i, infile in enumerate(sys.argv[2:-1]):
  lead_times = []
  c = colors[i]
  try:
    predictions = map(string.strip, file(infile).readlines())
    gold_standard = map(string.strip, file(sys.argv[-1]).readlines())
  except:
    print "usage: prediction_assessment.py predictions gold_standard"
    sys.exit()

#sort predictions to match the order of the gold standard
  ordering = dict(zip([g.split()[0] for g in gold_standard], xrange(len(gold_standard))))
  predictions.sort(key=lambda x: ordering[x.split()[0]])

  results = []
  for pred, gold in zip(predictions, gold_standard):
    #predictions may be accompanied with a time
    try:
      p_vid, p_val, p_time = pred.split(' ', 2)
      if p_time == 'None':
        p_time = None
      else:
        p_time = float(p_time)
    except:
      p_time = None
      p_vid, p_val = pred.split(' ', 2)



    try:
      g_vid, g_val = gold.strip().split()
    except:
      print gold, 'could not parse'
      sys.exit()
    
    if p_time and int(g_val) == 1:
      lead_times.append(-p_time/60.0)
      print -p_time/60.0
    results.append((int(g_val), float(p_val)))

  plt.figure(1)
  print 'median lead_times', np.median(lead_times)
  y_true,y_score = zip(*results)
  fpr, tpr, thresh = precision_recall_curve(y_true, y_score)
  for z in zip(fpr, tpr, thresh):
    print 'precision, recall',z

  plt.plot(fpr,tpr, c+'*', markersize=10, label=labels[c])
  plt.title('Precision-Recall', fontsize=30)
  plt.xlabel('precision', fontsize=30)
  plt.ylabel('recall',fontsize=30)
  plt.legend(fontsize=20)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  
  plt.figure(2)
  fpr, tpr,thresh =roc_curve(y_true, y_score)
  #for z in zip(fpr, tpr, thresh):
  #  print '1-spec, sense', z
  plt.plot(fpr,tpr, c+'*', markersize=10, label=labels[c])
  plt.title('ROC curve', fontsize=30)
  plt.xlabel('1-specificity', fontsize=30)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  plt.legend(fontsize=20)
  plt.ylabel('recall', fontsize=30)

  plt.figure(3)
  try:
    plt.hist(lead_times, bins=range(0,6*60, 10), label=labels[c])
    plt.xticks(range(0,6*60,60), fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylabel('Count', fontsize=30)
    plt.title('Lead time', fontsize=30)
    plt.xlabel('Lead time (minutes)', fontsize=30)
  except:
    pass

if name == 'none':
  plt.show()
  sys.exit()

plt.figure(1)
plt.tight_layout()
plt.savefig('figures/'+name+'-pr.pdf')
plt.figure(2)
plt.tight_layout()
plt.savefig('figures/'+name+'-roc.pdf')
plt.figure(3)
plt.tight_layout()
plt.savefig('figures/'+name+'-lt.pdf')
