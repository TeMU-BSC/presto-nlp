

import json


def main():
    # import the types annotated file
    with open('presto_types.jsonl', 'r') as fin:
        data = list(map(json.loads, fin.readlines()))

    ids_counter = {}

    print(len(data))

    # check which instances have been annotated by the three annotators
    for line in data:
        if line['id'] in ids_counter.keys():
            if line['_annotator_id'] not in ids_counter[line['id']][1]:
                ids_counter[line['id']][0] += 1
                ids_counter[line['id']][1].append(line['_annotator_id'])
        else:
            annotator = [line['_annotator_id']]
            ids_counter[line['id']] = [1, annotator]

    good_ids = []
    for key,value in ids_counter.items():
        if value[0] == 3:
            good_ids.append(key)

    print(len(good_ids))

    # check if preanotator also said distorsion
    already_there = []

    good_lines =[]
    for line in data:
        if line['id'] in good_ids and line['pre-ann-category']['distortion'] == 'distorsión':
            if (line['id'], line['_annotator_id']) not in already_there:
                already_there.append((line['id'], line['_annotator_id']))
                good_lines.append(line)

    print(len(good_lines))

    num_final_ids =[]
    for line in good_lines:
        num_final_ids.append(line['id'])
    print(len(list(set(num_final_ids))))

    # save those in a json of the exact same format
    with open('types_de_los_coincidentes.jsonl', 'w') as out:
       for line in good_lines:
           out.write(json.dumps(line) + "\n")


main()