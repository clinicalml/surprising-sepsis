import csv
import numpy as np

labels = {}
for l in file('patients/train_sepsis_labels.txt'):
  mrn, label = l.split()
  labels[mrn] = int(label)
for l in file('patients/test_sepsis_labels.txt'):
  mrn, label = l.split()
  labels[mrn] = int(label)


outcomes = [[],[]]
for l in csv.reader(file('data/golive.csv')):
  mrn = l[0].strip()
  live = l[1]
  outcomes[int(live)].append(labels[mrn])
  

print 'before live', np.mean(outcomes[0]), 'N=', len(outcomes[0])
print 'after live', np.mean(outcomes[1]), 'N=', len(outcomes[1])
