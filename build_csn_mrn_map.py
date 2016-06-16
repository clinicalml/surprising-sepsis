from collections import defaultdict
import cPickle as pickle

infile = file('data/SEPSIS_COHORT_2013-2014.DEID.csv')

infile.readline()
mrn_to_csn = defaultdict(list)
csn_to_mrn = {}
for l in infile:
    mrn,csn,_ = l.split(',',2)
    mrn_to_csn[mrn].append(csn)
    csn_to_mrn[csn] = mrn

print len(mrn_to_csn), 'mrn values'
pickle.dump(mrn_to_csn, file('patients/mrn_to_csn.pk', 'w'))
pickle.dump(csn_to_mrn, file('patients/csn_to_mrn.pk', 'w'))

outfile = file('patients/all_csn', 'w')
for csn in csn_to_mrn:
  print >>outfile, csn
outfile.close()
