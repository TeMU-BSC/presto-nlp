import pandas as pd
from typing import Tuple, List


def postprocess_sentences(sentence: str) -> str:
    return sentence.strip('.').strip().lower()


def read_rc_data(file) -> Tuple[List[str], list]:
    rc_data = pd.ExcelFile(file)

    distorsions = []
    sentences = []
    for distorsion in rc_data.sheet_names:
        sents = [postprocess_sentences(sent) for sent in rc_data.parse(distorsion)['Ejemplos Distorsión']
                     if not pd.isna(sent)]

        distorsions.extend([distorsion] * len(sents))
        sentences.extend(sents)

    return sentences, distorsions

