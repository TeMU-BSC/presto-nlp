import subprocess
import pandas as pd
import jsonlines
import json

for level in ['distortion', 'types']:
        if level == 'distortion':
                an_file = f"--an-file /home/casimiro/presto-nlp/presto_anotaciones/presto_distortion.dedup.jsonl" 
        elif level == 'types':
                an_file = f"--an-file /home/casimiro/presto-nlp/presto_anotaciones/types_de_los_coincidentes.jsonl" 

        print('XAVI MIREIA')
        cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
                --level {level} --metrics single_cohen multi_cohen exact_cohen --an-ids xavi mireia
                {an_file}'''
        subprocess.run(cmd.split())

        print('MIRIAM MIREIA')
        cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
                --level {level} --metrics single_cohen multi_cohen exact_cohen --an-ids miriam mireia
                {an_file}'''
        subprocess.run(cmd.split())

        print('XAVI MIREIA')
        cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
                --level {level} --metrics single_cohen multi_cohen exact_cohen --an-ids xavi miriam
                {an_file}'''
        subprocess.run(cmd.split())

        print('XAVI PRE_ANN')
        cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
                --level {level} --metrics single_cohen multi_cohen exact_cohen --an-ids xavi
                {an_file}
                --pre_annotations'''
        subprocess.run(cmd.split())

        print('MIRIAM PRE_ANN')
        cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
                --level {level} --metrics single_cohen multi_cohen exact_cohen --an-ids miriam
                {an_file}
                --pre_annotations'''
        subprocess.run(cmd.split())

        print('MIREIA PRE_ANN')
        cmd = f'''python /home/casimiro/presto-nlp/presto_anotaciones/evaluate.py
                --level {level} --metrics single_cohen multi_cohen exact_cohen --an-ids mireia
                {an_file}
                --pre_annotations'''

        subprocess.run(cmd.split())

        eval_file = f'/home/casimiro/presto-nlp/presto_anotaciones/cohens_scores_{level}.jsonl'
        table_file = f'/home/casimiro/presto-nlp/presto_anotaciones/cohens_scores_{level}.csv'

        scores = {}
        with jsonlines.open(eval_file) as reader:
            for ann in reader:
                scores.update(ann)
        df = pd.read_json(json.dumps(scores), orient='index')

        with open(table_file, 'w') as f:
            df.to_csv(f)
