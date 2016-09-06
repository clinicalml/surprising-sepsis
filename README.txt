These files are used to read patient data and train random forest classifiers to predict risk of sepsis.

Patient data is recorded in timeline form. Every piece of information is recorded with a timestamp so
we know when it becomes available to the surveillance algorithm. Our goal is to predict
the likelihood of sepsis before it is "too late". Our current definition of too late is when the physician
demonstrates suspicion of infection by ordering a lactate lab test or antibiotics.

When training, we sample points uniformly from the patient timelines and use them in a random forest classifier.
When testing, we continuously predict, updating the prediction every time a new piece of information becomes available.
- A positive prediction occurs if we predict a value above a threshold before it's too late.
- Otherwise the prediction is considered negative.
- By varying that threshold we obtain an ROC and precision-recall curve.
- For any threshold, we can also determine how far before the deadline would the simulated alert fire.

A few files are already assumed to exist:
  data files in csv format
  labels (run build_labels.py)
  train/test split (run build_train_test_split.py)
  mappings between csn and mrns (run build_csn_mrn_map.py)
  preprocessed patient demographics (run build_demographic_vectors.py)

Main training pipeline:
-----------------------

build_patient_timelines.py
  * reads patient data from data directory and stores in a shelf file for indexed access.

build_deadlines.py
  * reads from visit shelf and determines the "too late" time for each patient.
  * condition for "too late" is contained in function cutoff_record at the top of the file.

decision_tree_learning.py
  * reads patient records and builds feature vectors
  * learns a random forest classifier

decision_tree_testing.py
  * runs the learned decision tree on the test patient timelines, re-evaluating patients every
    time a new piece of information becomes available. Records the maximum value of predicted risk
    as well as first time classifier goes above a specified alerting threshold

roc.py
  * Uses the output of decision_tree_testing to build an roc and precision recall curve 
    and compares to simple 2/6 SIRS alerting approaches.

Other important files
--------------------
  Patient.py
    * Describes the Patient representation object
    * Each new data record updates the internal state of
      the Patient object
  
  generate_vectors.py
    * Generate all feature vectors for a single patient 
    (i.e., one new feature vector every time a new piece 
    of data becomes available.)

  utils.py
    * a number of useful utility functions
