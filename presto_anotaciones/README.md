
## Annotation for the PRESTO project

First, set env variables

```
export PRODIGY_CONFIG=prodigy.json
export PRODIGY_ALLOWED_SESSIONS=annotator1,annotator2
export PRODIGY_PORT=8080
```

Remove previous databases 

```
prodigy drop presto_distortion
prodigy drop presto_type
```
### Anotate if it has a distortion
Launch the annotation server on the URLs of the type: "http://localhost:PRODIGY_PORT/?session=annotator1"
```
prodigy textcat.choice_with_comment -E presto_distortion all_data.jsonl --label distorsión,"no distorsión" -F textcat.py
```
### Anotate the type of distortion

```
prodigy textcat.multiple_nested presto_type presto_distortion -F textcat.py
```

### Evaluation
Extract the annotation from the databases

```
prodigy db-out presto_distortion > presto_distortion.jsonl
prodigy db-out presto_type > presto_type.jsonl
```

```
python evaluate.py --level first --an1-id ANN1 --an2-id ANN2 --an-file presto_distortion.jsonl

python evaluate.py --level second --metrics single_cohen,multi_cohen,exact_cohen --an1-id ANN1 --an2-id ANN2 --an-file presto_type.jsonl
```