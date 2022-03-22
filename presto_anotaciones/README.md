
## Annotation for the PRESTO project
Remove previous databases 

```
prodigy drop presto_distortion
prodigy drop presto_type
```
### Anotate if it has a distortion

```
prodigy textcat.manual -E presto_distortion datos.7.jsonl --label distorsión,"no distorsión"
```

When done with the day save like: 

```
prodigy db-out presto_distortion > presto_first_level.jsonl
```

### Anotate the type of distortion

```
prodigy textcat-modified presto_type presto_first_level.jsonl -F recipe.py
```

When done with the day save like: 

```
prodigy db-out presto_type > presto_final.jsonl
```