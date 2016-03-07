from collections import defaultdict
import sys
import scipy.sparse as sparse
import numpy as np

def isnumeric(x):
  try:
    float(x)
    return True
  except:
    return False

  
def extract_temporal_features(v):
    #(count, mean, min, max, delta from mean)
    if None in v:
      return 5, [len(v), 0, 0, 0, 0]

    try:
      mean = np.mean(v)
    except:
      print 'cannot compute mean', v
      sys.exit()
    return 5, [len(v), mean, np.min(v), np.max(v), v[-1] - mean]

  
class Patient:

  def __init__(self, pid=None, vid=None, inv_vocab={}, alert_conditions={}, dry_run=False):
    try:
      self.vid = int(vid)
      self.pid = int(pid)
    except:
      self.vid = None
      self.pid = None

    self.dry_run = dry_run
    self.alert_conditions = alert_conditions
    self.inv_vocab = inv_vocab
    self.alert_counter = defaultdict(int)
    self.clinical_state = {'history':defaultdict(list), 'current':defaultdict(list)}
    self.cohort_info = None

    idx_jump,_ = extract_temporal_features([None])
    self.feature_vector = sparse.dok_matrix((1,len(inv_vocab)*2*idx_jump))
    self.dense_feature_vector = np.zeros((1,len(inv_vocab)*2*idx_jump+1))
    self.temporal_state = 'history'

  def is_interesting(self, record):
    for phrase in ['LABS-recorded', 'VITALS-measured', 'MENTAL-measured']:
      if phrase in record['comment']:
        return True
    return False

  def update_state(self, record):
    change = False
    if self.pid:
      assert record['mrn'][0] == self.pid, record

    alerts = []
    for alert, (condition,lim) in self.alert_conditions.items():
      if condition(self, record) and self.alert_counter[alert] < lim:
        alerts.append(alert)
        self.alert_counter[alert] += 1

    if self.is_interesting(record):
      #Update temporal state
      if record['csn'][0] == self.vid:
        self.temporal_state = 'current'

      elif self.temporal_state == 'current':
        self.temporal_state = 'future'
        #hard-coded alert for discharge time
        alerts.append('discharge')

      if self.temporal_state == 'future':
        #early return if temporal_state is future
        alerts.append('future')
        return alerts, change


      change = True
      var = record['description'][0]
      if var == 'BP': #special case for blood pressure
        val  = record['result'][0]
        if len(val):
          try:
            sbp = float(val.split('/')[0])
            self.update_state_helper('SBP',sbp)
            dbp = float(val.split('/')[1])
            self.update_state_helper('DBP',dbp)
          except:
            print 'funny BP value', val
            pass
      else:

        try:
          val = record['result'][0]
        except:
          val = None
          pass

        for v in val.split(';'):
          self.update_state_helper(var,v)

    return alerts, change
  
  def get_state(self):
    return self.clinical_state

  def update_state_helper(self, var, val):    

    if not isnumeric(val):
      var = var + ':'+val
      val = None
    else:
      val = float(val)

    self.clinical_state[self.temporal_state][var].append(val)
    if self.dry_run == True:
      return True

    if not var in self.inv_vocab:
      return False

    v = self.clinical_state[self.temporal_state][var]
    idx_jump, features = extract_temporal_features(v)
    idx = self.inv_vocab[var]*(2*idx_jump)

    if self.temporal_state == 'current':
      idx += idx_jump
    
    for j,val in zip(xrange(idx, idx+idx_jump), features):
      self.dense_feature_vector[0,j] = val
    self.dense_feature_vector[0,-1] += 1 # num-edits
    return True
      
  def get_combined_state(self):
    state = defaultdict(list)
    for k,v in self.clinical_state['history'].items() + self.clinical_state['current'].items():
      state[k].append(v)
    return state
  
  def get_vector(self, inv_vocab):
    return sorted([(j,val) for (i,j),val in self.feature_vector.items()])

