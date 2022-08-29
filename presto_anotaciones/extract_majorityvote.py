
import json

def main():
    with open('presto_distortion.jsonl', 'r') as fin:
        data = list(map(json.loads, fin.readlines()))

    uniq_ids = list(set([line['id'] for line in data]))
    uniq_text = list(set([line['text'] for line in data]))
    if len(uniq_text) == len(uniq_ids):
        ValueError("Text and ids should have the same length")

    final_labels = []
    for t,id in enumerate(uniq_ids):
        votes = [0, 0, 0]  # blank, distorsion, no distorsion
        result = []
        instance = []
        for line in data:
            if line['id'] == id:
                instance.append(line)
        if len(instance) == 3:
            #print(instance)
            for i in instance:
                if len(i['accept']) == 0:
                    votes[0] += 1
                elif i['accept'][0] == 'distorsión':
                    votes[1] += 1
                elif i['accept'][0] == 'no distorsión':
                    votes[2] += 1

        for i,vote in enumerate(votes):
            if vote >= 2:
                if i == 0:
                    result = []
                if i == 1:
                    result = ['distorsión']
                if i == 2:
                    result = ['no distorsión']

            # save this to a json in the right format for annotation and call it truth_distortion.jsonl
        final_labels.append({'id':id, 'text':uniq_text[t], 'accept':result})
    with open('truth_distortion.jsonl', 'w') as out:
        for line in final_labels:
            out.write(json.dumps(line) + "\n")


main()