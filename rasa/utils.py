import re
import pandas as pd
from pathlib import Path


def lookup_to_regex(items):
    """
    Convert a list of items meant for lookup matching to regex matching

    :param file: path to the file with the items to match, one per line
    :return: regex: regular expression that match the items
    """
    regex = r'\b(' + r'|'.join(items) + r')\b'

    return regex


def parse_csv(file):
    """
    Parsing file containing relevant items to match and print out the regex expression to perform the match
    :param file: path to the file containing the items
    """

    filepath = Path(file)

    # File-specific parsing
    if filepath.name == 'noms_de_persona.csv':
        df = pd.read_csv(filepath, skiprows=7, encoding='latin-1', delimiter=';')
        items = []
        for name in df['Nom']:
            if '/' in name:
                for subname in name.split('/'):
                    items.append(subname.lower())
            else:
                items.append(name.lower())

    # Assuming one item per line format
    else:
        with open(filepath, encoding='latin-1') as fn:
            items = [item.strip() for item in fn.readlines()]

    return items


if __name__ == '__main__':
    noms_nombres = parse_csv('nombres-noms/noms_de_persona.csv') + parse_csv('nombres-noms/Nombres (Firstnames).txt')
    regex_noms_nombres = lookup_to_regex(noms_nombres)
    print(regex_noms_nombres)
