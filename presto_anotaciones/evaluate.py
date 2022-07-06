import json
from sklearn.metrics import cohen_kappa_score
import numpy as np
import argparse
from scipy import spatial
import os
from nltk.metrics.agreement import AnnotationTask
import copy


def parsing_arguments(parser):
    parser.add_argument("--an-ids", type=str,
                        help='ids of all the annotators commas separated')
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

    for label in labels:  # por cada label, vamos por todas las instancias y miramos si están
        label_vector, _ = dict_for_each_ann(annotators)
        for id in list_ids:
            instance = [d for d in data if d['id'] == id]
            if len(instance) == len(annotators):
                for an in range(len(annotators)):
                    if label in instance[an]['accept']:
                        label_vector[names_dicts[an]].append(1)
                    else:
                        label_vector[names_dicts[an]].append(0)
        for an in range(len(annotators)):
            vectors[names_dicts[an]].append(label_vector[names_dicts[an]])
    return vectors, names_dicts


def evaluate_cohen(vectors, labels, annotators):
    scores, names_dicts = dict_for_each_ann(annotators)
    for num_an, an in enumerate(names_dicts):
        compare = ['a', 'b']
        for i, label in enumerate(labels):
            # this prevents the model from failing if we don't have data of all the labels
            if num_an != len(names_dicts)-1:
                compare = [annotators[num_an], annotators[num_an + 1]]
            else:
                compare = [annotators[0], annotators[len(annotators)-1]]
            if vectors[compare[0]][i] != [0] * len(vectors[compare[0]][i]):
                score = cohen_kappa_score(
                    np.array(vectors[compare[0]][i]), np.array(vectors[compare[1]][i]))
                print('Cohen Kappa for \'{}\' between {} and {}: {}'.format(
                    label, compare[0], compare[1], score))
                scores[an].append(score)
        print('Average Cohen Kappa between {} and {}: {}'.format(
            compare[0], compare[1], np.mean(scores[an])))


def cosine_distance(vec1, vec2):
    distance = spatial.distance.cosine(vec1, vec2)
    return distance


def evaluate_multi_cohen(vectors, annotators):
    # https://stats.stackexchange.com/questions/511927/interrater-reliability-with-multi-rater-multi-label-dataset
    task_data, names_dicts = dict_for_each_ann(annotators)
    for num_an, an in enumerate(names_dicts):
        # task_data = []
        if num_an != len(names_dicts) - 1:
            compare = [annotators[num_an], annotators[num_an + 1]]
        else:
            compare = [annotators[0], annotators[len(annotators) - 1]]
        for i, entry in enumerate(vectors[compare[0]]):
            annotation = 'coder_a', i, tuple(entry)
            task_data[an].append(annotation)
        for i, entry in enumerate(vectors[compare[1]]):
            annotation = 'coder_b', i, tuple(entry)
            task_data[an].append(annotation)
        # https://www.nltk.org/_modules/nltk/metrics/agreement.html
        cosine_task = AnnotationTask(
            data=task_data[an], distance=cosine_distance)
        print("Fleiss's Kappa using Cosine distance between {} and {}: {}".format(
            compare[0], compare[1], cosine_task.multi_kappa()))


def evaluate_exact_cohen(data, annotators):

    annotations, list_annotators = dict_for_each_ann(annotators)
    list_ids = list(set([d['id'] for d in data]))
    for id in list_ids:
        instance = [d for d in data if d['id'] == id]
        if len(instance) == len(annotators):
            for an in range(len(annotators)):
                annotations[list_annotators[an]].append(
                    str(instance[an]['accept']))
        else:
            print('One annotator is missing annotation', id)
    if len(annotators) == 2:
        import pdb
        pdb.set_trace()
        print('Exact Cohen Kappa:', cohen_kappa_score(
            annotations[list_annotators[0]], annotations[list_annotators[1]]))
    else:
        for i in range(len(annotators)-1):
            print(list_annotators[i], 'versus', list_annotators[i+1])
            print('Exact Cohen Kappa:',
                  cohen_kappa_score(annotations[list_annotators[i]], annotations[list_annotators[i+1]]))
        print(list_annotators[0], 'versus', list_annotators[len(annotators)-1])
        print('Exact Cohen Kappa:', cohen_kappa_score(
            annotations[list_annotators[0]], annotations[list_annotators[len(annotators)-1]]))


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

    # Select data for given list of annotators.
    # In the case of multiple annotators, get the intersection of annotations

    ann_ids_intersection = set(ann['id'] for ann in data)
    for annotator_name in list_annotators:
        ann_ids_intersection = ann_ids_intersection.intersection([ann['id'] for ann in data
                                                                  if ann['_annotator_id'] == f"presto_{args.level}-{annotator_name}"])

    data_annotators = []
    for ann in data:
        for annotator_name in list_annotators:
            if ann['_annotator_id'] == f"presto_{args.level}-{annotator_name}" and ann['id'] in ann_ids_intersection:
                data_annotators.append(ann)

    perc_examples = round(len(ann_ids_intersection) /
                          len(set(ann['id'] for ann in data))*100, 2)
    print(f"Computing scores on {perc_examples}% of the total examples)")

    # get pre-annotation (from one of the annotators since they share the same pre-annotations),
    # replace the "accept" field with the value of pre-annotation and change annotator and session fields
    if args.pre_annotations:

        data_preann = copy.deepcopy(data_annotators)
        # the preannotations should be just considered once
        one_example_of_each = data_preann[0]['_annotator_id']
        for d in data_preann:
            if d['_annotator_id'] == one_example_of_each:
                # the pre-annotation is a string in the "distorsion" level while is a list in the "types" level
                # TODO: change the format while parsing the original data
                if isinstance(d['pre-ann-category'][args.level], str):
                    d['accept'] = [d['pre-ann-category'][args.level]]
                else:
                    d['accept'] = d['pre-ann-category'][args.level]
                d.pop('pre-ann-category')
                d['_annotator_id'] = 'pre-annotator'
                d['_session_id'] = 'pre-annotator'
                data_annotators.append(d)

        list_annotators.append('pre-annotator')

    if args.level == 'distortion':
        evaluate_exact_cohen(data_annotators, list_annotators)

    if args.level == 'types':
        labels = ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                  'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                  'razonamiento emocional', 'personalización']
        vectors, names_dicts = create_label_vectors(
            data_annotators, labels, list_annotators)

        # FOR EACH LABEL, CALCULATE COHEN KAPPA
        if 'single_cohen' in list_metrics:
            evaluate_cohen(vectors, labels, names_dicts)

        # FOR EACH ANNOTATION, SEE IF THE LABELS ARE EXACTLY THE SAME
        if 'exact_cohen' in list_metrics:
            evaluate_exact_cohen(data_annotators, list_annotators)

        # FOR EACH ANNOTATION, SEE HOW SIMILAR THE ANNOTATIONS ARE (VECTOR SIMILARITY APPROACH)
        if 'multi_cohen' in list_metrics:
            evaluate_multi_cohen(vectors, names_dicts)
            # there is a warning, but it might be because of the zeros
            # issue when there is few data: 0s are also counted as similarity


if __name__ == '__main__':
    main()
