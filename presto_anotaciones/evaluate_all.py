import subprocess
import pandas as pd
import jsonlines
import json

print('XAVI MIREIA')
cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
        --level types --metrics single_cohen multi_cohen exact_cohen --an-ids xavi mireia
        --an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl'''
subprocess.run(cmd.split())

print('MIRIAM MIREIA')
cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
        --level types --metrics single_cohen multi_cohen exact_cohen --an-ids miriam mireia
        --an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl'''
subprocess.run(cmd.split())

print('XAVI MIREIA')
cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
        --level types --metrics single_cohen multi_cohen exact_cohen --an-ids xavi miriam
        --an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl'''
subprocess.run(cmd.split())

print('XAVI PRE_ANN')
cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
        --level types --metrics single_cohen multi_cohen exact_cohen --an-ids xavi
        --an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl
        --pre_annotations'''
subprocess.run(cmd.split())

print('MIRIAM PRE_ANN')
cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
        --level types --metrics single_cohen multi_cohen exact_cohen --an-ids miriam
        --an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl
        --pre_annotations'''
subprocess.run(cmd.split())

print('MIREIA PRE_ANN')
cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
        --level types --metrics single_cohen multi_cohen exact_cohen --an-ids mireia
        --an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl
        --pre_annotations'''

subprocess.run(cmd.split())

eval_file = '/home/casimiro/presto-nlp/presto_anotaciones/cohens_scores.jsonl'
table_file = '/home/casimiro/presto-nlp/presto_anotaciones/cohens_scores.csv'

scores = {}
with jsonlines.open(eval_file) as reader:
    for ann in reader:
        scores.update(ann)
df = pd.read_json(json.dumps(scores), orient='index')

with open(table_file, 'w') as f:
    df.to_csv(f)
