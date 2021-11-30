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
file = '../data/cognitive-distorsions/RC_data.xlsx'
sentences, distorsions = read_rc_data(file)
sentence_embeddings = model.encode(sentences)

knn = KNeighborsClassifier(n_neighbors=15)
knn.fit(sentence_embeddings, distorsions)
with open('knn-model.pkl', 'wb') as fn:
    pickle.dump(knn, fn)

pca = PCA(n_components=2)
sentence_embeddings_reduc = pca.fit_transform(sentence_embeddings)


# plt.scatter()

while True:
    test_sentence = str(input('Type sentence below:\n'))
    test_embedding = model.encode(test_sentence)\
        if isinstance(model.encode(test_sentence), list) else [model.encode(test_sentence)]
    print(f"Predicted distorsion: {knn.predict(test_embedding)}")
