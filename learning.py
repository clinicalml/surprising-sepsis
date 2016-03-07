from sklearn.datasets import load_svmlight_file
from sklearn.tree import DecisionTreeClassifier
import datetime


X_train, Y_train = load_svmlight_file('output/train_patient_vectors.svmlight')
clf = DecisionTreeClassifier()
clf.fit(X_train.todense(), Y_train)

X_test, Y_test = load_svmlight_file('output/test_patient_vectors.svmlight')
query_id = [l.split()[0] for l in file('patients/test_sepsis_labels.txt').readlines()]

Y_pred = clf.predict(X_test.todense())
outfile = file('output/decision_tree_predictions.txt', 'w')
for y,qid in zip(Y_pred, query_id):
    if y > 0:
        print >>outfile, qid, 1, datetime.datetime(datetime.MAXYEAR,1,1)
    else:
        print >>outfile, qid, 0
outfile.close()
