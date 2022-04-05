
## Annotation for the PRESTO project

First, set env variables

```
export PRODIGY_CONFIG=prodigy.json
export PRODIGY_ALLOWED_SESSIONS=annotator1,annotator2
```

Remove previous databases 

```
prodigy drop presto_distortion
prodigy drop presto_type
```
### Anotate if it has a distortion

```
prodigy textcat.manual -E presto_distortion datos.jsonl --label distorsión,"no distorsión"
```
### Anotate the type of distortion

```
prodigy textcat-modified presto_type presto_distortion -F recipe.py
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