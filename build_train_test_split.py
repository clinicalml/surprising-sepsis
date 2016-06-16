import random
import sys

random.seed(100)
working_dir = sys.argv[1]

patients = file(working_dir+'/patients/sepsis_labels.txt').readlines()
random.shuffle(patients)
N = len(patients)
train = patients[:int(0.8*N)]
test = patients[int(0.8*N):]

outfile = file(working_dir+'/patients/train_sepsis_labels.txt', 'w')
outfile.write(''.join(train))
outfile.close()

outfile = file(working_dir+'/patients/test_sepsis_labels.txt', 'w')
outfile.write(''.join(test))
outfile.close()
