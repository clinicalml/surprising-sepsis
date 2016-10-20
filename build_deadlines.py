import shelve
import os
from multiprocessing import Pool
import sys
import cPickle as pickle
import datetime
from utils import expand, sortkey

def cutoff_record(record):
  if record['comment'][0].lower() == "antibiotics":
    return True
  if 'description' in record and "lactate" in record['description'][0].lower() and not 'poc' in record['description'][0].lower():
    return True
  #print record, 'description' in record and "lactate" in record['description'][0].lower()
  return False

def find_start_end(records, csn):
  records = filter(lambda r: r['comment'][0] == "COHORT" and r['csn'][0] == csn, records)
  if len(records) > 1:
    pass
    #print 'too many records?'
    #print records
  if len(records) == 0:
    print 'no records?'
    print csn

  return records[0]['admission'][0], records[0]['discharge'][0]

working_dir = sys.argv[1]
all_csn = map(int, file(working_dir+'/patients/cohort_csn').readlines())
visitShelf = shelve.open(working_dir+'/patients/visitShelf')
csn_to_mrn = pickle.load(file(working_dir+'/patients/csn_to_mrn.pk'))

def compute_times(vid):
  pid = csn_to_mrn[str(vid)]
  record = visitShelf[str(pid)]
  start, end = find_start_end(record, vid)
  #end_time = find_end(record, vid)

  record = filter(lambda x: 'csn' in x and x['csn'][0] == vid and cutoff_record(x), record)
  record = expand(record)
  #for r in sorted(record, key=sortkey):
  #  if 'ordered' in r:
  #    print r['ordered'][0], r
  #  elif 'start' in r:
  #    print r['start'][0], r
  #  else:
  #    print r

  if len(record) == 0:
    cutoff_time = datetime.datetime(datetime.MAXYEAR,1,1)
  else:
    r = min(record, key=sortkey)
    if 'start' in r:
      cutoff_time = r['start'][0]
    elif 'ordered' in r:
      cutoff_time = r['ordered'][0]
    else:
      print "record has no start", r
      sys.exit()
  return  vid, start, end, cutoff_time

outfile = file(working_dir+'/patients/times', 'w')
#outfile = file(os.devnull, 'w')
pool = Pool(48)
for i, (vid,start,end,cutoff_time) in enumerate(pool.imap(compute_times, all_csn)):
#for i,csn in enumerate(all_csn):
#  vid, start,end,cutoff_time = compute_times(csn)
  if i % 1000 == 0:
    print i
    outfile.flush()
  print >>outfile, vid, start, end, cutoff_time

outfile.close()
