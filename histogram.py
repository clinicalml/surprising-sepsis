#!/usr/bin/python2.6
import matplotlib.pyplot as plt
import sys

X = []
for l in sys.stdin:
  X.append(float(l))

plt.hist(X, xrange(1,60*12,10))
plt.xticks(xrange(1,60*12,60), range(12), fontsize=20)
plt.yticks(fontsize=20)
plt.ylabel('Count', fontsize=20)
plt.xlabel('Hours until recognition', fontsize=20)
plt.tight_layout()
plt.savefig('figures/headroom.pdf')
