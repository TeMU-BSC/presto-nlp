from email.policy import default
import json
from sklearn.metrics import cohen_kappa_score
import numpy as np
import argparse
from scipy import spatial
from nltk.metrics.agreement import AnnotationTask
from collections import defaultdict
import copy
import os
import jsonlines


def parsing_arguments(parser):
    parser.add_argument("--an-ids", nargs='+',
                        help='List of annotator\' names.')
    parser.add_argument("--an-file", type=str,
                        help='file containing annotations')
    parser.add_argument("--metrics", nargs='+',
                        help='Options can be: single_cohen,exact_cohen,multi_cohen, write them comma-separated')
    parser.add_argument("--level",
                        choices=['distortion', 'types'],
                        help='Select the annotation level')
    parser.add_argument("--pre_annotations",
                        action='store_true',
                        help='Compute metrics including pre-annotations.')
    parser.add_argument("--intersection",
                        action='store_true',
                        help='Get common annotations by intersecting across all the annotators')
    return parser


def dict_for_each_ann(annotators):
    output = {}
    names_dicts = []
    for an in range(len(annotators)):
        name = annotators[an]
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


def evaluate_cohen(vectors, labels, annotators, multi=False):
    """Compute Cohen's Kappa score (for 2 annotators) in the case of single-label and multi-label annotations.
    By default, when multi==False  it returns the coefficient per labels and the average coefficient across all the labels.
    If multi==Tre, it returns the coefficient across all labels taking into account a measure of distance using the cosine similarity, 
    based on: https://stats.stackexchange.com/questions/511927/interrater-reliability-with-multi-rater-multi-label-dataset

    Args:
        vectors (Dict[List[List]]):  containing  the agreements for each label for each example
        labels (List): List of label names
        annotators (List): List of annotator names
        multi (Bool): Set the cosine distance for multi-label computation
    """
    score_labels = {}
    if not multi:

        for i, label in enumerate(labels):
            compare = [annotators[0], annotators[1]]
            if vectors[compare[0]][i] != [0] * len(vectors[compare[0]][i]):
                score_labels[label] = cohen_kappa_score(
                    np.array(vectors[annotators[0]][i]), np.array(vectors[annotators[1]][i]))
                print(F'Cohen\' kappa for \'{label}\': {score_labels[label]}')
        score_labels_avg = np.mean(list(score_labels.values()))
        score_labels.update({'single-label-average': score_labels_avg})
        print(f'Average cohen\' kappa: {score_labels_avg}')

    else:
        # Add task data for the annotators pair
        task_data = []
        for i, entry in enumerate(vectors[annotators[0]]):
            annotation = 'coder_a', i, tuple(entry)
            task_data.append(annotation)
        for i, entry in enumerate(vectors[annotators[1]]):
            annotation = 'coder_b', i, tuple(entry)
            task_data.append(annotation)

        # https://www.nltk.org/_modules/nltk/metrics/agreement.html
        cosine_task = AnnotationTask(data=task_data, distance=cosine_distance)
        score = cosine_task.kappa()
        score_labels['multi-label-cosine'] = score
        print(f"Cohen's Kappa using Cosine distance: {score}")

    return score_labels


def cosine_distance(vec1, vec2):
    distance = spatial.distance.cosine(vec1, vec2)
    return distance


# TODO: add docstring and refactor code
def evaluate_exact_cohen(data, annotators):
    score_labels = {}
    annotations, list_annotators = dict_for_each_ann(annotators)
    list_ids = sorted(list(set([d['id'] for d in data])))

    for id in list_ids:
        instance = [d for d in data if d['id'] == id]
        if len(instance) == len(annotators):
            for an in range(len(annotators)):
                annotations[list_annotators[an]].append(
                    str(instance[an]['accept']))
        else:
            print('One annotator is missing annotation', id)
    score = cohen_kappa_score(
        annotations[list_annotators[0]], annotations[list_annotators[1]])
    score_labels['multi-label-exact'] = score
    print('Exact Cohen\'s Kappa', cohen_kappa_score(
        annotations[list_annotators[0]], annotations[list_annotators[1]]))
    return score_labels


def main(args):
    with open(args.an_file, 'r') as fin:
        data = list(map(json.loads, fin.readlines()))

    list_metrics = args.metrics
    list_annotators = args.an_ids

    # Select data for given list of annotators.
    # In the case of multiple annotators, get the intersection of annotations
    ann_ids_intersection = set(ann['id'] for ann in data)
    for annotator_name in list_annotators:
        ann_ids_intersection = ann_ids_intersection.intersection([ann['id'] for ann in data
                                                                  if ann['_annotator_id'] == f"presto_{args.level}-{annotator_name}"])

    data_annotators = []
    for ann in data:
        for annotator_name in list_annotators:
            if ann['_annotator_id'] == f"presto_{args.level}-{annotator_name}":
                    if args.intersection:
                        if ann['id'] in ann_ids_intersection:
                            data_annotators.append(ann)
                    else:
                        data_annotators.append(ann)

    print(f"Computing scores on {len(ann_ids_intersection)/len(args.an_ids)} total examples")

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

                # lowercase the annotations
                d['accept'] = [d.lower() for d in d['accept']]
                d.pop('pre-ann-category')
                d['_annotator_id'] = 'pre-annotator'
                d['_session_id'] = 'pre-annotator'
                data_annotators.append(d)

        list_annotators.append('pre-annotator')

    assert len(list_annotators) == 2, ValueError(
        f'The script supports only metrics for 2 annotators but {len(list_annotators)} were passed.')

    scores = defaultdict(dict)
    annotators_pair = "-".join(args.an_ids)

    if args.level == 'distortion':
        score = evaluate_exact_cohen(data_annotators, list_annotators)
        # rename the dict key for clarity
        score['exact'] = score.pop('multi-label-exact')
        scores[annotators_pair].update(score)


    if args.level == 'types':
        labels = ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                  'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                  'razonamiento emocional', 'personalización']
        vectors, names_dicts = create_label_vectors(
            data_annotators, labels, list_annotators)

        # FOR EACH LABEL, CALCULATE COHEN KAPPA
        if 'single_cohen' in list_metrics:
            score = evaluate_cohen(vectors, labels, names_dicts)
            scores[annotators_pair].update(score)

        # FOR EACH ANNOTATION, SEE HOW SIMILAR THE ANNOTATIONS ARE (VECTOR SIMILARITY APPROACH)
        if 'multi_cohen' in list_metrics:
            score = evaluate_cohen(vectors, labels, names_dicts, multi=True)
            scores[annotators_pair].update(score)
            # there is a warning, but it might be because of the zeros
            # issue when there is few data: 0s are also counted as similarity

        # FOR EACH ANNOTATION, SEE IF THE LABELS ARE EXACTLY THE SAME
        if 'exact_cohen' in list_metrics:
            score = evaluate_exact_cohen(data_annotators, list_annotators)
            scores[annotators_pair].update(score)

    scores = dict(scores)
    # write to file
    eval_file = os.path.join(os.path.dirname(args.an_file), f'cohens_scores_{args.level}.jsonl')
    with jsonlines.open(eval_file, 'a') as f:
        f.write(scores)

if __name__ == '__main__':
    # TODO: poner errores cuando un anotador no tenga ninguna anotación
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()

    main(args)

