
source ../venv/bin/activate
export PRODIGY_CONFIG=prodigy.json
export PRODIGY_ALLOWED_SESSIONS=mireia,miriam,xavi
PRODIGY_PORT=8081 prodigy textcat.hierarchical_multiple -E presto_annotation second_phase/RC_data_to_annotate_90%.jsonl --label distorsión,"no distorsión" -F textcat_distortion.py