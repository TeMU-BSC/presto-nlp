## Annotation for the PRESTO project

First, set env variables

```
export PRODIGY_CONFIG=prodigy.json
export PRODIGY_ALLOWED_SESSIONS=casimiro,blanca
```

Remove previous datasets and sessions

```
prodigy drop presto_distortion-blanca
prodigy drop presto_distortion-casimiro
prodigy drop presto_types-blanca
prodigy drop presto_types-casimiro
```
### Anotate if it has a distortion
Launch the annotation server on the URLs of the type: "http://localhost:PRODIGY_PORT/?session=<username>"
```
PRODIGY_PORT=8081 prodigy textcat.choice_with_comment -E presto_distortion all_data.jsonl --label distorsión,"no distorsión" -F textcat_distortion.py
```
### Before the second round of annotation the majority vote should be calculated

TODO

### Anotate the type of distortion

```
PRODIGY_PORT=8081 prodigy textcat.multiple_nested presto_types presto_distortion casimiro -F textcat_distortion.py
PRODIGY_PORT=8082 prodigy textcat.multiple_nested presto_types presto_distortion blanca -F textcat_distortion.py
```

### Evaluation
Extract the annotation from the databases

```
prodigy db-out presto_distortion > presto_distortion.jsonl
prodigy db-out presto_types > presto_types.jsonl
```

```
python evaluate.py --level distortion --an-ids blanca,casimiro --an-file presto_distortion.jsonl --pre_annotations

python evaluate.py --level types --metrics single_cohen,multi_cohen,exact_cohen --an-ids blanca,casimiro --an-file presto_types.jsonl --pre_annotations
```