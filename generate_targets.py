from utils import *
import datetime
from Patient import Patient
import shelve
import numpy as np
import cPickle as pickle
import random



#create a random set of patient ids with a set number of
#positive labels (cases), negative labels (controls), alerts.
#if test is true, use all of the test patients.
def generate_targets(n_cases=0, n_controls=0, n_alerts=0, test=False, directory='.'):

  patients_dir = directory+'/patients'
  output_dir = directory+'/output'

  csn_to_mrn = pickle.load(file(patients_dir+'/csn_to_mrn.pk'))
  alert_csns = set()
  case_csns = set()
  control_csns = set()

  if test:
    label_file = patients_dir+'/test_sepsis_labels.txt'
  else:
    label_file = patients_dir+'/train_sepsis_labels.txt'
    if n_alerts > 0:
      for l in file(output_dir+'/alert_predictions.txt'):
        csn = l.split()[0]
        label = l.split()[1]
        if label == '1':
          alert_csns.add(csn)

  for l in file(label_file):
    csn = l.split()[1]
    label = l.split()[2]
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
