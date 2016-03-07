import cPickle as pickle


vocab, inv_vocab = pickle.load(file('output/new-vocab.pk'))
for v in vocab:
  print v, inv_vocab[v]
