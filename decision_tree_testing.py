import cPickle as pickle
from multiprocessing import Pool
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm
import numpy as np
from generate_targets import *
from generate_vectors import *
from sklearn.metrics import roc_curve, precision_recall_curve

if __name__ == "__main__":
  predictor = pickle.load(file(sys.argv[1])) 
  def eval((X,Y)):
    X = np.vstack([x[1] for x in X])
    pred = predictor.predict_proba(X)
    pred = pred[:,1].max()
    y = Y[0]
    return pred, y

  test_targets = generate_targets(test=True)
  vector_generator = VectorGenerator()
  y_true = []
  y_score = []
  pool = Pool(32)
  vectors = vector_generator.generate(test_targets, processes=32)
  N = len(test_targets)
  for i, (y_hat,y) in tqdm(enumerate(pool.imap(eval, vectors)), total=N):
    y_true.append(y)
    y_score.append(y_hat)
  
  fpr, tpr, thresh = roc_curve(y_true, y_score)
  prec, recall, thres = precision_recall_curve(y_true, y_score)
  
  plt.figure('ROC')
  plt.title('ROC')
  plt.plot(fpr, tpr)

  plt.figure('PR curve')
  plt.title('Precision Recall')
  plt.plot(recall, prec)
  plt.xlabel('recall')
  plt.ylabel('precision')

  plt.show()
