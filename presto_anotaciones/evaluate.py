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
    #parser.add_argument("--n_annotators", type=int, default=2)
    parser.add_argument("--an-ids", type=str,
                        help='ids of all the annotators commas separated')
    #parser.add_argument("--an2-id", type=str,
    #                    help='annotator 2 id')
    parser.add_argument("--an-file", type=str,
                        help='file containing annotations')
    parser.add_argument("--metrics", default='single_cohen,exact_cohen,multi_cohen',
                        help='Options can be: single_cohen,exact_cohen,multi_cohen, write them comma-separated')
    parser.add_argument("--level", default='types', choices=['distortion', 'types'],
                        help='Select the annotation level')
    parser.add_argument("--pre_annotations", action='store_true')
    return parser

def dict_for_each_ann(annotators):
    output = {}
    names_dicts = []
    for an in range(len(annotators)):
        name = "annotator_{0}".format(annotators[an])
        names_dicts.append(name)
        output[name] = []
    return output, names_dicts

def create_label_vectors(data, labels, annotators):
    vectors, names_dicts = dict_for_each_ann(annotators)
    list_ids = list(set([d['id'] for d in data]))

    for label in labels: # por cada label, vamos por todas las instancias y miramos si están
        label_vector, _ = dict_for_each_ann(annotators)
        # done: go through each id, store different for each annotator
        for id in list_ids:
            instance = [d for d in data if d['id'] == id]
            if len(instance) == len(annotators):
                for an in range(len(annotators)):
                    if label in instance[an]['accept']:
                        label_vector[names_dicts[an]].append(1)
                    else:
                        label_vector[names_dicts[an]].append(0)
        #for line in data:
        #    if label in line['accept']:
        #        output_type_a.append(1)
        #    else:
        #        output_type_a.append(0)
        for an in range(len(annotators)):
            vectors[names_dicts[an]].append(label_vector[names_dicts[an]])
    return vectors, names_dicts


def evaluate_cohen(vectors, labels, annotators):
    # TODO: allow multiple annotators
    scores = []
    for i, label in enumerate(labels):
        # this prevents the model from failing if we don't have data of all the labels
        if vectors[annotators[0]][i] != [0] * len(vectors[annotators[0]][i]):
            score = cohen_kappa_score(
                np.array(vectors[annotators[0]][i]), np.array(vectors[annotators[1]][i]))
            print('Cohen Kappa for \'{}\': {}'.format(label, score))
            scores.append(score)
    print('Average Cohen Kappa per label:', np.mean(scores))


def cosine_distance(vec1, vec2):
    distance = spatial.distance.cosine(vec1, vec2)
    return distance


def evaluate_multi_cohen(vectors, annotators):
    # TODO: allow multiple annotators
    # https://stats.stackexchange.com/questions/511927/interrater-reliability-with-multi-rater-multi-label-dataset
    task_data = []
    for i, entry in enumerate(vectors[annotators[0]]):
        annotation = 'coder_a', i, tuple(entry)
        task_data.append(annotation)
    for i, entry in enumerate(vectors[annotators[1]]):
        annotation = 'coder_b', i, tuple(entry)
        task_data.append(annotation)
    # https://www.nltk.org/_modules/nltk/metrics/agreement.html
    cosine_task = AnnotationTask(data=task_data, distance=cosine_distance)
    print(f"Fleiss's Kappa using Cosine distance: {cosine_task.multi_kappa()}")


def evaluate_exact_cohen(data, annotators):
    annotations, list_annotators = dict_for_each_ann(annotators)
    list_ids = list(set([d['id'] for d in data]))
    for id in list_ids:
        instance = [d for d in data if d['id']==id]
        if len(instance) == len(annotators):
            for an in range(len(annotators)):
                annotations[list_annotators[an]].append(str(instance[an]['accept']))
        else:
            print('One annotator is missing annotation', id)
    if len(annotators) == 2:
        print('Exact Cohen Kappa:', cohen_kappa_score(annotations[list_annotators[0]], annotations[list_annotators[1]]))
    else:
        for i in range(len(annotators)-1):
            print(list_annotators[i], 'versus', list_annotators[i+1])
            print('Exact Cohen Kappa:',
                  cohen_kappa_score(annotations[list_annotators[i]], annotations[list_annotators[i+1]]))
        print(list_annotators[0], 'versus', list_annotators[len(annotators)-1])
        print('Exact Cohen Kappa:', cohen_kappa_score(annotations[list_annotators[0]], annotations[list_annotators[len(annotators)-1]]))

def main():
    # TODO: poner errores cuando un anotador no tenga ninguna anotación
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.an_file, 'r') as fin:
        data = list(map(json.loads, fin.readlines()))

    list_metrics = args.metrics.split(',')
    list_annotators = args.an_ids.split(',')
    # TODO: allow for the preannotations to be evaluated
    # get pre-annotation (from one of the annotators since they share the same pre-annotations),
    # replace the "accept" field with the value of pre-annotation and change annotator and session fields
    if args.pre_annotations:
        data_preann = copy.deepcopy(data)
        one_example_of_each = data_preann[0]['_annotator_id'] # the preannotations should be just considered once
        for d in data_preann:
            if d['_annotator_id'] == one_example_of_each:
                d['accept'] = d['pre-ann-category'][args.level]
                d.pop('pre-ann-category')
                d['_annotator_id'] = 'pre-annotator'
                d['_session_id'] = 'pre-annotator'
                data.append(d)
        list_annotators.append('pre-annotator')

    if args.level == 'distortion':
        evaluate_exact_cohen(data, list_annotators)

    if args.level == 'types':
        labels = ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                  'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                  'razonamiento emocional', 'personalización']
        vectors, names_dicts = create_label_vectors(data, labels, list_annotators)

        # FOR EACH LABEL, CALCULATE COHEN KAPPA
        if 'single_cohen' in list_metrics:
            evaluate_cohen(vectors, labels, names_dicts)

        # FOR EACH ANNOTATION, SEE IF THE LABELS ARE EXACTLY THE SAME
        if 'exact_cohen' in list_metrics:
            evaluate_exact_cohen(data, list_annotators)

        # FOR EACH ANNOTATION, SEE HOW SIMILAR THE ANNOTATIONS ARE (VECTOR SIMILARITY APPROACH)
        if 'multi_cohen' in list_metrics:
            evaluate_multi_cohen(vectors, names_dicts)
            # there is a warning, but it might be because of the zeros
            # issue when there is few data: 0s are also counted as similarity


if __name__ == '__main__':
    main()
