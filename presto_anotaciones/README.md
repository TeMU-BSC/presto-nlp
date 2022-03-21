
## Annotation for the PRESTO project

### Anotate if it has a distortion

```
prodigy textcat.manual presto_distortion presto-nlp/presto_anotaciones/datos-jsonl.jsonl --label yes,no
```

When done with the day save like: 

```
prodigy db-out presto_distortion > presto_first_level.jsonl
```

### Anotate the type of distortion

```
prodigy textcat-modified presto_type presto_distortion.jsonl -F recipe.py
```

When done with the day save like: 

```
prodigy db-out presto_type > presto_final.jsonl
```