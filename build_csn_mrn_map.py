from collections import defaultdict
import cPickle as pickle

infile = file('data/SEPSIS_COHORT_2013-2014_2.DEID.csv')

infile.readline()
mrn_to_csn = defaultdict(list)
csn_to_mrn = {}
for l in infile:
    mrn,csn,_ = l.split(',',2)
    mrn_to_csn[mrn].append(csn)
    csn_to_mrn[csn] = mrn

pickle.dump(mrn_to_csn, file('mrn_to_csn.pk', 'w'))
pickle.dump(csn_to_mrn, file('csn_to_mrn.pk', 'w'))
