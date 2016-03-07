import random

random.seed(100)
patients = file('patients/sepsis_labels.txt').readlines()
random.shuffle(patients)
N = len(patients)
train = patients[:int(0.8*N)]
test = patients[int(0.8*N):]

outfile = file('patients/train_sepsis_labels.txt', 'w')
outfile.write(''.join(train))
outfile.close()

outfile = file('patients/test_sepsis_labels.txt', 'w')
outfile.write(''.join(test))
outfile.close()
