import datetime
from Patient import Patient
import shelve
import numpy as np
import cPickle as pickle
import random



#utility to change date strings that appear in the records
#to python datetime objects
def to_date(d):
  try:
    return datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
  except:
    return datetime.datetime.strptime(d, "%Y/%m/%d %H:%M:%S")



#sort primarily by date
#secondary sorting so that alerts go after the data that
#that triggered them is present.
def sortkey(e):
    if 'time' in e and not None in e['time']:
        return (e['time'][0], 'ALERTS' in e['comment'][0])
    else:
        return (datetime.datetime(datetime.MINYEAR,1,1), True)

#util to build an inverse vocab that maps words to indices.
def invert_vocab(v):
    return dict(zip(v, xrange(len(v))))


#expand records. If multiple timestamps exist for a single 
#record (e.g., sample ordered, sample taken, value recorded),
#break into multiple records.
def expand(records):
  l = []
  for r in records:
    for k,val in r.items():
      if type(val[0]) == datetime.datetime:
        entry = dict(r)
        entry['comment']= (entry['comment'][0]+'-'+k,)
        entry['time'] = val
        l.append(entry)
  return l



