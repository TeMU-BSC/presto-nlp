# Script to compute error analysis on annotations
from argparse import ArgumentParser
import jsonlines
import pandas as pd
from collections import defaultdict, Counter

def obs_agreement(ann):
    labels = []
    for key in ann.keys():
        if key != 'text':
            labels.extend(ann[key])
    if labels:
        obs_agreement = Counter(labels).most_common(1)[0][1]
    else:
        print(f"Empty annotation: {ann}")
        obs_agreement = ''
    return obs_agreement 
            


if __name__ == '__main__':
        
    for level in ['distortion', 'types']:
        file_ann_level = f'/home/casimiro/presto-nlp/presto_anotaciones/presto_{level}.jsonl'
        file_errors = f'/home/casimiro/presto-nlp/presto_anotaciones/errors_{level}.csv'


        # add text and annotation labels for pre-annotations and all the annotators
        table_rows = defaultdict()
        with jsonlines.open(file_ann_level) as pre_ann:
            for ann in pre_ann:
                table_row = defaultdict()
                table_row['text'] = ann['text']
                # table_row['id'] = ann['id']
                if level == 'types':
                    table_row['pre_annotation'] = [ann for ann in ann['pre-ann-category'][level]]
                else:
                    table_row['pre_annotation'] = [ann['pre-ann-category'][level]]
                table_rows[ann['id']] = table_row

        with jsonlines.open(file_ann_level) as ann_level:
            for ann in ann_level:
                ann_name = ann['_annotator_id'].split('-')[1]
                table_rows[ann['id']][ann_name] = ann['accept']


        for ann in table_rows.values():
            agreement = obs_agreement(ann)
            if agreement:
                ann.update({'agreement': agreement})
            else:
                ann.update({'Rejected': 'Yes'})
        
        table_rows = dict(table_rows)
        df = pd.DataFrame.from_records(list(table_rows.values()), index=list(table_rows.keys()))
        df.to_csv(file_errors)
