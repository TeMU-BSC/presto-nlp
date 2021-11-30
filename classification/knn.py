"""
This code computes sentences embedding and run KNN algorithm.
It is partially taken from: https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/computing-embeddings/computing_embeddings.py
"""
from sentence_transformers import SentenceTransformer, LoggingHandler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from utils import read_rc_data
import numpy as np
import logging
import pickle
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', type=float, default=0.1,
                        help='confidence threshold for multi-label classification')
    parser.add_argument('--multi-label', action='store_true',
                        help='returns multi-label classification based on threshold value')
    parser.add_argument('--neighbors', type=float, default=15,
                        help='number of neighbors for KNN model')
    args = parser.parse_args()

    # Just some code to print debug information to stdout
    np.set_printoptions(threshold=100)

    logging.basicConfig(format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        handlers=[LoggingHandler()])
    # /print debug information to stdout

    # Load pre-trained Sentence Transformer Model. It will be downloaded automatically
    # model = 'distiluse-base-multilingual-cased-v1'  # best model for Spanish STS
    model = 'distiluse-base-multilingual-cased-v2'
    model = SentenceTransformer(model)

    # Embed a list of sentences
    file = '/home/casimiro/projects/presto-nlp/data/cognitive-distorsions/RC_data.xlsx'
    sentences, distorsions = read_rc_data(file)
    sentence_embeddings = model.encode(sentences)

    knn = KNeighborsClassifier(n_neighbors=args.neighbors)
    knn.fit(sentence_embeddings, distorsions)
    with open('knn-model.pkl', 'wb') as fn:
        pickle.dump(knn, fn)

    pca = PCA(n_components=2)
    sentence_embeddings_reduc = pca.fit_transform(sentence_embeddings)

    while True:
        test_sentence = [str(input('Type sentence below:\n'))]
        test_embedding = model.encode(test_sentence)

        pred_probs = {p: l for p, l in zip(
            knn.predict_proba(test_embedding)[0], knn.classes_)}

        pred_multi_labels_threshold = {label: prob for prob,
                                       label in pred_probs.items() if prob > args.threshold}
        pred_multi_labels_threshold = sorted(
            pred_multi_labels_threshold.items(), key=lambda item: item[1], reverse=True)

        if args.multi_label:
            print(f"Predicted distorsion: {pred_multi_labels_threshold}")
        else:
            print(f"Predicted distorsion: {pred_multi_labels_threshold[0]}")
