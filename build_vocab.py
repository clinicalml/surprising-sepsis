from Patient import Patient
from multiprocessing import Pool
import sys
import shelve
from collections import Counter, defaultdict
from utils import sortkey, invert_vocab, to_date, expand
from generate_targets import generate_targets
import cPickle as pickle



workdir = sys.argv[1]
try:
  threshold = int(sys.argv[w])
except:
  threshold = 10


def get_state((label, pid, vid)):
  patient = Patient(pid, vid, dry_run=True)
  #print 'pid/vid', pid, vid
  for e in sorted(expand(s[pid]), key=sortkey):
    alerts, change = patient.update_state(e)
    if 'future' in alerts:
      break
  return patient.get_combined_state()

train_targets = generate_targets(n_cases=2500, n_controls=2500, directory=workdir)
s = shelve.open(workdir+'/patients/visitShelf')
key_counter = Counter()
pool = Pool(48)
for i,state in enumerate(pool.imap(get_state, train_targets)):
#for i, tar in enumerate(train_targets):
  #state = get_state(tar)
  if i % 100 == 0:
    print i
    print state.keys()
  key_counter.update(state.keys())


vocab,counts = zip(*filter(lambda x: x[1] > threshold, key_counter.items()))
inv_vocab = invert_vocab(vocab)
pickle.dump((vocab, inv_vocab), file(workdir+'/output/vocab.pk', 'w'))
