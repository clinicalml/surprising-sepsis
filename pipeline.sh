set -e
WORKDIR=$1

python set_up_dir.py $WORKDIR
python build_csn_mrn_map.py $WORKDIR
python build_labels.py $WORKDIR
python build_train_test_split.py $WORKDIR
python build_demographic_vectors.py $WORKDIR
python build_patient_timelines.py $WORKDIR
python build_deadlines.py $WORKDIR
python build_vocab.py $WORKDIR
python decision_tree_learning.py $WORKDIR
python decision_tree_testing.py $WORKDIR
