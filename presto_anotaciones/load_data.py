import csv
import json
import sys
import os
import random

random.seed(33)

def main(input_file, output_file):
    with open(input_file) as input_file:
        content = csv.reader(input_file, quotechar='"')
        data = list(content)[1:]

    examples_annotation = []
    with open(output_file, 'w') as out:
        category_to_out = {'distorsión': 'distorsión',
                           'tricky': 'no distorsión', 
                           'alternativo': 'no distorsión'}
        for instance in data:
            list_distortions = []
            for t in instance[3:7]:
                if t:
                    list_distortions.append(t)

            examples_annotation.append({'id': instance[0],
                    'text': instance[1], 
                    'types': [],
                    'pre-ann-category': {
                        'distortion': category_to_out[instance[2]],
                        'types': list_distortions}})

        # shuffle data
        random.shuffle(examples_annotation)
        for example in examples_annotation:
            out.write(json.dumps(example) + "\n")


if __name__ == '__main__':
    input_file = os.path.realpath(sys.argv[1])
    output_file = os.path.realpath(sys.argv[2])
    main(input_file, output_file)
