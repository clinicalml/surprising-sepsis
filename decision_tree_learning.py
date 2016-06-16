import numpy as np
import random
import sys
import cPickle as pickle
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from generate_targets import *
from generate_vectors import *

random.seed(100)

training_targets = generate_targets(2500, 2500)

X_train = []
Y_train = []

vector_generator = VectorGenerator()
for i, (X,Y) in enumerate(vector_generator.generate(training_targets, processes=48)):
  X = [x[1] for x in X]
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

param_grid = {'max_depth':range(5,50,5), 
              'min_samples_leaf':range(5,25,5), 
              'n_estimators':[10], 
              'n_jobs':[10], 
              'class_weight':['balanced_subsample']
              }

pipeline = Pipeline([
    ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False, C=0.1))),
    ('forest', GridSearchCV(RandomForestClassifier(), param_grid, n_jobs=10, scoring='accuracy'))
    ])

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

pipeline.fit(X_train, Y_train)
print 'classifier trained'

pickle.dump(pipeline, file('output/classifier-pipeline.pk', 'w'))
