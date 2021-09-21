import pandas as pd
from typing import Dict
from collections import defaultdict
import json
import yake


def postprocess_sentences(sentence: str) -> str:
    return sentence.strip('.').strip().lower()


def extract_keywords(file, max_ngram_size, num_kw, deduplication) -> Dict:
    """
    Read examples of distorsion from the excel file and
    store them in a dictionary structure `distorsion_type --> sentences`
    and extract keywords

    :param file:
    :param max_ngram_size:
    :param num_kw:
    :param deduplication:
    :return:
    """
    rc_data = pd.ExcelFile(file)
    distorsions = rc_data.sheet_names
    distorted_keywords = defaultdict(dict)
    kw_extractor = yake.KeywordExtractor(lan='es',
                                         n=max_ngram_size,
                                         top=num_kw,
                                         dedupLim=deduplication)
    for distorsion in distorsions:
        sentences = [postprocess_sentences(sent) for sent in rc_data.parse(distorsion)['Ejemplos Distorsión']
                     if not pd.isna(sent)]

        # distorted_keywords[distorsion]['sentences'] = sentences

        sentences_concat = '. '.join(sentences)
        distorted_keywords[distorsion]['keywords'] = list(kw_extractor.extract_keywords(sentences_concat))

    return distorted_keywords


if __name__ == '__main__':
    max_ngram_size = 1
    num_kw = 10
    deduplication = 0.9
    distorted_keywords = extract_keywords('../data/RC_data.xlsx', max_ngram_size, num_kw, deduplication)
    conf = f"{max_ngram_size}_{num_kw}_{deduplication}"
    with open(f'distorted_keywords_{conf}.json', 'w') as fn:
        json.dump(distorted_keywords, fn)

