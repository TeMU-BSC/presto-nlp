
source ../venv/bin/activate
export PRODIGY_CONFIG=prodigy.json
export PRODIGY_ALLOWED_SESSIONS=gerard,casimiro
PRODIGY_PORT=8081 prodigy textcat.hierarchical_multiple -E presto_annotation first_phase/all_data.jsonl --label distorsión,"no distorsión" -F textcat_distortion.py