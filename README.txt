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

Assumes that data files are available in csv format

Main training pipeline (see pipeline.sh):
-----------------------
set_up_directory.py
  * creates a working directory where files will be stored
  * settings are copied from the settings/ directory into the working directory

build_csn_mrn_map.py -- builds a mapping between csns and mrns in the cohort
build_labels.py -- uses icd9 codes to determine a label for each visit
build_train_test_split.py -- randomly splits visits into train/test
build_demographic_vectors.py -- demographics are stored separately

build_patient_timelines.py
  * reads patient data from data directory and stores in a shelf file for indexed access.

build_deadlines.py
  * reads from visit shelf and determines the "too late" time for each patient.
  * condition for "too late" is contained in function cutoff_record at the top of the file.

build_vocab.py

decision_tree_learning.py
  * reads patient records and builds feature vectors
  * learns a random forest classifier

decision_tree_testing.py
  * runs the learned decision tree on the test patient timelines, re-evaluating patients every
    time a new piece of information becomes available. Records the maximum value of predicted risk
    as well as first time classifier goes above a specified alerting threshold

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
    * some useful utility functions

  fieldReader
    * A CSV reader that extracts important fields and maps to standard names

Settings directory
------------------
The settings directory has the following files:

  FIELDS.txt
    * gives the FieldReader the required information to parse CSV files
  FILES_TO_READ.txt
    * a list of files that will be the input from which to build patient representations
  SEPSIS_CRITERIA.txt
    * not used
  SEPSIS_ICD9
    * ICD9 codes used to define the sepsis outcome
