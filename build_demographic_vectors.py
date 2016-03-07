import sys
import cPickle as pickle
import shelve
from utils import to_date
import csv

infile = csv.reader(file('data/SEPSIS_COHORT_2013-2014_2.DEID.csv'))
header = infile.next()
arrival_times = ['ED_ARRIVED_TIME.DEID', 'ADM_DATE_TIME.DEID', 'IP_ADMIT_DATE_TIME.DEID', 'ED_TRIAGE_TIME.DEID', 'DISCH_TIME.DEID']

index = dict(zip(header, xrange(len(header))))
print index

patients = {}
races = set()
ethnicities = set()

for l in infile:
  mrn = l[index['MRN.DEID']]
  csn = l[index['CSN.DEID']]

  birthdate = l[index['BIRTH_DATE.DEID']]
  if birthdate == 'before_1925':
    birthdate = '1925/01/01 00:00:00'
  earliest_time = min([to_date(l[index[i]]) for i in arrival_times if len(l[index[i]])])
  age = (earliest_time - to_date(birthdate)).days / 365
  sex = l[index['GENDER']]
  race = l[index['RACE']]
  ethnicity = l[index['ETHNICITY']]
  patients[mrn, csn] = (age, sex, race, ethnicity)
  races.add(race)
  ethnicities.add(ethnicity)

races = sorted(races)
ethnicities = sorted(ethnicities)
race_index = dict(zip(races, xrange(len(races))))
ethnicity_index = dict(zip(ethnicities, xrange(len(ethnicities))))
print 'race', race_index
print 'ethnicity', ethnicity_index

K = len(races) + len(ethnicities)+3
def create_vector(patient_values):
  age, sex, race,ethnicity = patient_values
  vec = ['1:'+str(age)]
  if sex == 'M':
    vec.append('2:1')
  else:
    vec.append('3:1')
  vec.append(str(race_index[race]+3)+':1')
  vec.append(str(ethnicity_index[ethnicity]+3+len(race_index))+':1')
  return ' '.join(vec)

pickle.dump(ethnicities, file('patients/ethnicities.pk', 'w'))
pickle.dump(races, file('patients/races.pk', 'w'))

patient_vectors = shelve.open('patients/demographics')
for pat, vals in patients.items():
  patient_vectors[str(pat[1])] = create_vector(vals)

patient_vectors.close()
