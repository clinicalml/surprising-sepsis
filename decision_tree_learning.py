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

working_dir = sys.argv[1]
patients_dir = working_dir+'/patients'
output_dir = working_dir+'/output'


vocab, _ = pickle.load(file(output_dir+'/vocab.pk'))
ethnicities = pickle.load(file(patients_dir+'/ethnicities.pk'))
races = pickle.load(file(patients_dir+'/races.pk'))
feature_names = []
feature_names.extend(['', 'age', 'Male', 'Female']+['race:'+r for r in races]+['ethnicity:'+e for e in ethnicities])
for v in vocab:
    for time in ['hist', 'curr']:
        feature_names.extend([time+'-count-'+v, time+'-mean-'+v, time+'-min-'+v, time+'-max-'+v, time+'-recent-'+v])

feature_names.append('updates')
training_targets = generate_targets(2500, 10000, directory=working_dir)

X_train = []
Y_train = []

print 'generated targets'

vector_generator = VectorGenerator(working_dir=working_dir)
for i, (X,Y) in enumerate(vector_generator.generate(training_targets, processes=48)):
  X = [x[1] for x in X]
  X_train.extend(X)
  Y_train.extend(Y)
  if i%10 == 0:
    print i

print 'generated vectors'

print len(X_train)
print len(Y_train)
X_train = np.vstack(X_train)
Y_train = np.array(Y_train)

print Y_train.shape
print X_train.shape
print 'total training patients', Y_train.size, 'total positive cases', (Y_train > 0).sum()
  #pickle.dump((X_train, Y_train), file(patients_dir+'/training_examples.pk', 'w'))

param_grid = {'max_depth':range(5,50,5), 
              'min_samples_leaf':range(5,25,5), 
              'n_estimators':[10,50,100], 
              'n_jobs':[10], 
              'class_weight':['balanced_subsample']
              }

pipeline = Pipeline([
    ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False, C=0.1))),
    ('forest', GridSearchCV(RandomForestClassifier(), param_grid, n_jobs=10, scoring='accuracy'))
    ])

print len(feature_names), X_train.shape

#for x in X_train:
#  print filter(lambda z: z[1] > 0, zip(feature_names, x))

pipeline.fit(X_train, Y_train)
print 'classifier trained'

pickle.dump(pipeline, file(output_dir+'/classifier-pipeline.pk', 'w'))
