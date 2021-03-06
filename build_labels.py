import string
import sys
from collections import defaultdict
import cPickle as pickle
from fieldReader import FieldReader

# The goal of this script is to output the MRN/CSNs of patients who have sepsis
# according to our definition.

def extract_from(record, inclusion):
  return (r for r in record if r['comment'][0].lower() in inclusion)


working_dir = sys.argv[1]
reader = FieldReader('data/SEPSIS_DX_2013-2014.DEID.csv', fields=working_dir+'/settings/FIELDS.txt')

sepsis_patients = defaultdict(set)
sepsis_criteria = set(map(string.strip, file(working_dir+'/settings/SEPSIS_ICD9').readlines()))
all_csn = map(int, file(working_dir+'/patients/cohort_csn').readlines())
csn_to_mrn = pickle.load(file(working_dir+'/patients/csn_to_mrn.pk'))

for i,p in enumerate(reader):

  pid = p['mrn'][0]
  vid = p['csn'][0]
  if vid == 7:
    print p

  if i % 10000 == 0:
    print i

  if p['description'][0] in sepsis_criteria:
    sepsis_patients[vid].add(p['description'][0])
  
outfile = file(working_dir+'/patients/sepsis_labels.txt', 'w')
for vid in sorted(all_csn):
    pid = csn_to_mrn[str(vid)]
    if vid in sepsis_patients:
      print >>outfile, pid, vid, 1, ';'.join(sepsis_patients[vid])
    else:
      print >>outfile, pid, vid, 0
