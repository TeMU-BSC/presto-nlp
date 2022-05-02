import json
from sklearn.metrics import cohen_kappa_score
import numpy as np
import argparse
from scipy import spatial
import os
from nltk.metrics.agreement import AnnotationTask
import copy
# from sklearn.preprocessing import MultiLabelBinarizer # I don't use it, but it would make sense for the vectors


def parsing_arguments(parser):
    parser.add_argument("--an1-id", type=str,
                        help='annotator 1 id')
    parser.add_argument("--an2-id", type=str,
                        help='annotator 2 id')
    parser.add_argument("--an-file", type=str,
                        help='file containing annotations')
    parser.add_argument("--metrics", default='single_cohen,exact_cohen,multi_cohen',
                        help='Options can be: single_cohen,exact_cohen,multi_cohen, write them comma-separated')
    parser.add_argument("--level", default='types', choices=['distortion', 'types'],
                        help='Select the annotation level')
    parser.add_argument("--pre_annotations", action='store_true')
    return parser


def create_label_vectors(data, labels):
    type_a = []
    for label in labels:
        output_type_a = []
        for line in data:
            if label in line['accept']:
                output_type_a.append(1)
            else:
                output_type_a.append(0)
        type_a.append(output_type_a)
    return type_a


def evaluate_cohen(vectors_1, vectors_2, labels):
    scores = []
    for i, label in enumerate(labels):
        # this prevents the model from failing if we don't have data of all the labels
        if vectors_1[i] != [0] * len(vectors_1[i]):
            score = cohen_kappa_score(
                np.array(vectors_1[i]), np.array(vectors_2[i]))
            print('Cohen Kappa for \'{}\': {}'.format(label, score))
            scores.append(score)
    print('Average Cohen Kappa per label:', np.mean(scores))


def cosine_distance(vec_a, vec_b):
    distance = spatial.distance.cosine(vec_a, vec_b)
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
    # https://www.nltk.org/_modules/nltk/metrics/agreement.html
    cosine_task = AnnotationTask(data=task_data, distance=cosine_distance)
    print(f"Fleiss's Kappa using Cosine distance: {cosine_task.multi_kappa()}")


def evaluate_exact_cohen(data, data2):
    out1 = []
    out2 = []
    for line in data:
        # could be improved, this would fail with order change
        out1.append(str(line['accept']))
    for line2 in data2:
        out2.append(str(line2['accept']))
    print('Exact Cohen Kappa:', cohen_kappa_score(out1, out2))


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.an_file, 'r') as fin:
        data = list(map(json.loads, fin.readlines()))

        an_file_suffix = os.path.splitext(os.path.basename(args.an_file))[0]
        data1 = [d for d in data
                 if d["_annotator_id"] == f"{an_file_suffix}-{args.an1_id}"]
        data2 = [d for d in data
                 if d["_annotator_id"] == f"{an_file_suffix}-{args.an2_id}"]

        # get pre-annotation (from one of the annotators since they share the same pre-annotations),
        # replace the "accept" field with the value of pre-annotation and change annotator and session fields
        if args.pre_annotations:
            data_preann = copy.deepcopy(data1)
            for data in data_preann:
                data['accept'] = data['pre-ann-category'][args.level]
                data.pop('pre-ann-category')
                data['_annotator_id'] = 'pre-annotator'
                data['_session_id'] = 'pre-annotator'

    list_metrics = args.metrics.split(',')

    # TODO: implement the evaluation for more than 2 annotations
    if args.level == 'distortion':
        evaluate_exact_cohen(data1, data2)

    if args.level == 'types':
        labels = ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                  'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                  'razonamiento emocional', 'personalización']

        vectors_1 = create_label_vectors(data1, labels)
        vectors_2 = create_label_vectors(data2, labels)

        # METRIC, FOR EACH TYPE, CALCULATE COHEN KAPPA
        if 'single_cohen' in list_metrics:
            evaluate_cohen(vectors_1, vectors_2, labels)

        # FOR EACH ANNOTATION, SEE IF THE LABELS ARE EXACTLY THE SAME
        if 'exact_cohen' in list_metrics:
            evaluate_exact_cohen(data1, data2)

        # FOR EACH ANNOTATION, SEE HOW SIMILAR THE ANNOTATIONS ARE (VECTOR SIMILARITY APPROACH)
        if 'multi_cohen' in list_metrics:
            evaluate_multi_cohen(vectors_1, vectors_2)
            # there is a warning, but it might be because of the zeros
            # issue when there is few data: 0s are also counted as similarity


if __name__ == '__main__':
    main()
