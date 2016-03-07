from svmlight_loader import load_svmlight_file
import cPickle as pickle
import numpy as np

def summarize_col(X, j):
  non_zero = [float(x) for x in X[:, j] if x>0]
  if len(non_zero) == 0:
    return 'NONE'
  return ','.join([str(z) for z in [len(non_zero), min(non_zero)]+ [np.percentile(non_zero,q) for q in [25, 50, 75]]+[max(non_zero)]])

vocab, _ = pickle.load(file('output/vocab.pk'))
ethnicities = pickle.load(file('patients/ethnicities.pk'))
races = pickle.load(file('patients/races.pk'))

feature_names = ['age', 'Male', 'Female']+['race:'+r for r in races]+['ethnicity:'+e for e in ethnicities]
for v in vocab:
    for time in ['hist', 'curr']:
        feature_names.extend([time+'-count-'+v, time+'-min-'+v, time+'-mean-'+v, time+'-max-'+v])

for T in ['deadline', 'discharge']:
  outfile = file('patients/summary-'+T+'.csv', 'w')
  X_train, Y_train = load_svmlight_file('output/train_patient_vectors-'+T+'.svmlight')

  X_train = X_train.todense()
  X_pos = X_train[:2500, :]
  X_neg = X_train[2500:, :]

  print 3+len(ethnicities)+len(races)
  for j in xrange(X_pos.shape[1]):
    print >>outfile, ','.join(['"'+feature_names[j]+'"', summarize_col(X_pos, j), summarize_col(X_neg, j)])

