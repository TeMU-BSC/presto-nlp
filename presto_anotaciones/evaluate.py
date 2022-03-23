import json
from sklearn.metrics import cohen_kappa_score
import numpy as np
import argparse
from scipy import spatial
from nltk.metrics.agreement import AnnotationTask
#from sklearn.preprocessing import MultiLabelBinarizer # I don't use it, but it would make sense for the vectors

def parsing_arguments(parser):
    parser.add_argument("--an1", default='presto_final.jsonl')
    parser.add_argument("--an2",  default='presto_final.jsonl')
    parser.add_argument("--metrics", default='single_cohen', help='Options can be: single_cohen,exact_cohen,multi_cohen, write them comma-separated')
    parser.add_argument("--level", default='second', help='Options can be: first (distortion?), second (type)')
    return parser

def create_label_vectors(data, labels):
    type_a = []
    for label in labels:
        output_type_a = []
        for i, line in enumerate(data):
            if label in line['accept']:
                output_type_a.append(1)
            else:
                output_type_a.append(0)
        type_a.append(output_type_a)
    return type_a

def evaluate_cohen(vectors_1, vectors_2, labels):
    scores = []
    for i, label in enumerate(labels):
        if vectors_1[i] != [0] * len(vectors_1[i]):  # this should be removed once we have data from all categories
            score = cohen_kappa_score(np.array(vectors_1[i]), np.array(vectors_2[i]))
            print('Cohen Kappa for \'{}\': {}'.format(label, score))
            scores.append(score)
    print('Average Cohen Kappa per label:', np.mean(scores))

def cosine_distance(vec_a,vec_b):
    distance = spatial.distance.cosine(vec_a,vec_b)
    return distance

def evaluate_multi_cohen(vec_a, vec_b):
    # https://stats.stackexchange.com/questions/511927/interrater-reliability-with-multi-rater-multi-label-dataset
    task_data = []
    for i, entry in enumerate(vec_a):
        annotation = 'coder_a', i, tuple(entry)
        task_data.append(annotation)
    for i, entry in enumerate(vec_b):
        annotation = 'coder_b', i, tuple(entry)
        task_data.append(annotation)
    cosine_task = AnnotationTask(data=task_data, distance=cosine_distance)
    print(f"Fleiss's Kappa using Cosine distance: {cosine_task.multi_kappa()}")

def evaluate_exact_cohen(data, data2):
    out1 = []
    out2 = []
    for line in data:
        out1.append(str(line['accept'])) #could be improved, this would fail with order change
    for line2 in data2:
        out2.append(str(line2['accept']))
    print('Exact Cohen Kappa:', cohen_kappa_score(out1, out2))


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.an1, 'r') as fin:
        data1 = list(map(json.loads, fin.readlines()))

    with open(args.an2, 'r') as fin: # this should be the other annotations
        data2 = list(map(json.loads, fin.readlines()))

    list_metrics = args.metrics.split(',')

    if args.level == 'first':
        distortion = []
    if args.level == 'second':
        labels = ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                    'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                    'razonamiento emocional', 'personalización']

        vectors_1 = create_label_vectors(data1, labels)
        vectors_2 = create_label_vectors(data2, labels)

        # METRIC, FOR EACH TYPE, CALCULATE COHEN KAPPA
        if 'single_cohen' in list_metrics:
            evaluate_cohen(vectors_1, vectors_2, labels)

        # TODO: METRIC, FOR EACH ANNOTATION, SEE IF THE LABELS ARE EXACTLY THE SAME
        if 'exact_cohen' in list_metrics:
            evaluate_exact_cohen(data1, data2)

        # TODO: METRIC, FOR EACH ANNOTATION, SEE HOW SIMILAR THE ANNOTATIONS ARE (VECTOR APPROACH)
        if 'multi_cohen' in list_metrics:
            evaluate_multi_cohen(vectors_1, vectors_2)
            # there is a warning, but it might be because of the zeros


if __name__ == '__main__':
    main()





