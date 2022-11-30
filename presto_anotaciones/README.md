## Annotation for the PRESTO project

First, set env variables

```
export PRODIGY_CONFIG=prodigy.json
export PRODIGY_ALLOWED_SESSIONS=casimiro,gerard
```

Remove previous datasets and sessions

```
prodigy drop presto_annotation-gerard
prodigy drop presto_annotation-casimiro
```
### Anotate distorsions in cascade

Launch the annotation server on the URLs of the type: "http://localhost:PRODIGY_PORT/?session=<username>"

```
PRODIGY_PORT=8081 prodigy textcat.hierarchical_multiple -E presto_annotation first_phase/all_data.jsonl --label distorsión,"no distorsión" -F textcat_distortion.py
```

### Evaluation

Extract the annotation from the databases

```
prodigy db-out presto_annotation > presto_annotation.jsonl


# TODO: check the command below
<!-- python agreement.py --level distortion --an-ids casimiro gerard --an-file presto_annotation.jsonl

python agreement.py --level types --metrics single_cohen multi_cohen exact_cohen --an-ids casimiro gerard --an-file types_de_los_coincidentes.jsonl --pre_annotations
``` -->