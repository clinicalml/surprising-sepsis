from utils import to_date

headroom = []
positive_cases = set()
for l in file('patients/sepsis_labels.txt'):
  if l[-2] == '1':
    positive_cases.add(l.split()[0])

for l in file('patients/times'):
  pid = l.split()[0]
  if pid in positive_cases:
    arrival = l.split()[1:3]
    deadline = l.split()[5:]
    arrival = ' '.join(arrival)
    deadline = ' '.join(deadline)
    if 'None' in l:
      continue
    print (to_date(deadline) - to_date(arrival)).total_seconds() / 60

