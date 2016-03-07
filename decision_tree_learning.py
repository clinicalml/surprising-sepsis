from svmlight_loader import load_svmlight_file
from multiprocessing import Pool
import numpy as np
import scipy.sparse as sparse
import shelve
from Patient import Patient
import random
from utils import generate_targets, expand, to_date, sortkey, generate_vectors
import sys
from collections import defaultdict
import cPickle as pickle
from sklearn.grid_search import GridSearchCV
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
import datetime
from functools import partial

random.seed(100)


training_targets = generate_targets(2500, None)
deadlines = {}
for l in file('patients/times'):
  vid = l.split()[0]
  t = ' '.join(l.split()[-2:])
  deadlines[vid] = to_date(t)

X_train = []
Y_train = []
pool = Pool(48)
filtered_generate_vectors = partial(generate_vectors, apply_filter=False)

for i, (X,Y) in enumerate(pool.imap(filtered_generate_vectors, [(pid, vid, label, 10) for (label, pid, vid) in training_targets])):
  X = np.array([x[1] for x in X])
  X_train.extend(X)
  Y_train.extend(Y)
  if i%1000 == 0:
    print i

print len(X_train)
print len(Y_train)
X_train = np.vstack(X_train)
Y_train = np.array(Y_train)

print Y_train.shape
print X_train.shape
print 'total training patients', Y_train.size, 'total positive cases', (Y_train > 0).sum()
if 'tree' in sys.argv:
  param_grid = {'max_depth':[5], 'min_samples_leaf':range(10,30,5)}
  clf = GridSearchCV(DecisionTreeClassifier(), param_grid, n_jobs=25, scoring='accuracy')
else:

  param_grid = {'forest__max_depth':range(5,50,5), 
                'forest__min_samples_leaf':range(5,25,5), 
                'forest__n_estimators':[10], 
                'forest__n_jobs':[10], 
                'forest__class_weight':['balanced_subsample']
                }

  pipeline = Pipeline([
      ('feature_selection', SelectFromModel(LinearSVC(penalty="l1"))),
      ('forest', RandomForestClassifier())
      ])

  clf = GridSearchCV(pipeline, param_grid, n_jobs=10, scoring='accuracy')

vocab, _ = pickle.load(file('output/vocab.pk'))
ethnicities = pickle.load(file('patients/ethnicities.pk'))
races = pickle.load(file('patients/races.pk'))
feature_names = []
feature_names.extend(['', 'age', 'Male', 'Female']+['race:'+r for r in races]+['ethnicity:'+e for e in ethnicities])
for v in vocab:
    for time in ['hist', 'curr']:
        feature_names.extend([time+'-count-'+v, time+'-mean-'+v, time+'-min-'+v, time+'-max-'+v, time+'-recent-'+v])

feature_names.append('updates')
print len(feature_names), X_train.shape
print feature_names[:10]

clf.fit(X_train, Y_train)
print 'classifier trained'


if 'tree' in sys.argv:
  export_graphviz(clf.best_estimator_, 'output/tree-deadline.dot', feature_names=feature_names)
else:
  pickle.dump(clf, file('output/decisiontree-deadline.pk', 'w'))
