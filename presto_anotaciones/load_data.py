import csv
import json


def main(filename):
    with open(filename) as file:
        content = csv.reader(file, quotechar='"')
        data = list(content)[1:]

    with open('all_data.jsonl', 'w') as out:
        category_to_out = {'distorsión': 'distorsión',
                           'tricky': 'no distorsión', 'alternativo': 'no distorsión'}
        for instance in data:
            list_distortions = []
            for t in instance[3:7]:
                if t:
                    list_distortions.append(t)

            info = {'id': instance[0], 'text': instance[1],
                    'pre-ann-category': {'distortion': category_to_out[instance[2]], 'types': list_distortions}}

            out.write(json.dumps(info) + "\n")


if __name__ == '__main__':
    filenane = '/home/casimiro/projects/presto-nlp/presto_anotaciones/RC_data_10%_random.csv'
    main(filenane)
