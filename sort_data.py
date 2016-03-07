import os
import sys

files = set(os.listdir('data'))
for f in list(files):
    if 'sorted' in f:
        files.discard(f)
        files.discard(f.replace('.sorted', ''))
    print f, os.path.isdir(f)
    if os.path.isdir('data/'+f):
        files.discard(f)

print 'sorting the following files', list(files)

for datafile in files:
    lines = file('data/'+datafile).readlines()
    header = lines[0]
    data = lines[1:]
    data.sort()
    outfile = file('data/'+datafile+'.sorted', 'w')
    outfile.write(header)
    outfile.write(''.join(data))
    outfile.close()


