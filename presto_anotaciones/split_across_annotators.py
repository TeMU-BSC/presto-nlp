"""Small script to split the annotations across annotators while balancing them."""
import json
import sys
import random
from collections import defaultdict
import numpy as np

random.seed(33)

# file_ann =sys.argv[1]
file_ann = "/home/ccasimiro/presto-nlp/presto_anotaciones/second_phase/RC_data_to_annotate_90%.jsonl"

with open(file_ann) as fn:
    data = [json.loads(line)
               for line in fn.readlines()]
    
    
id_types = defaultdict(list)
for ann in data:
    type = ann["id"].split("_")[0]
    id_types[type].append(ann["id"])

id_type_ann = defaultdict(list)
for type in id_types.keys():
    # assing a given type to annotators
    for split_id, split_type in enumerate(np.array_split(id_types[type], 3)):
        id_type_ann[f"ann_{split_id}"].extend(list(split_type))
id_type_ann = dict(id_type_ann)

for ann_id in id_type_ann.keys():
    with open(f"/home/ccasimiro/presto-nlp/presto_anotaciones/second_phase/RC_data_to_annotate_90%_{ann_id}.jsonl", "w") as fn:
        for ann in data:
            if ann["id"] in id_type_ann[ann_id]:
                fn.write(json.dumps(ann)+"\n")
