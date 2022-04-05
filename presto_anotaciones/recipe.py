import prodigy
from prodigy.components.loaders import JSONL
from typing import List, Optional
from prodigy.util import split_string
from random import shuffle
from prodigy.components.db import connect

hierarchy = {'distorsión': ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                            'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                            'razonamiento emocional', 'personalización'], 'no distorsión': []}

# from https://support.prodi.gy/t/does-prodigy-supports-hierarchical-annotation/1249/9


def get_stream(examples):
    for eg in examples:   # the examples with top-level categories
        top_labels = eg['accept']  # ['A'] or ['B', 'C'] if multiple choice
        for label in top_labels:
            if label != "no distorsión":
                sub_labels = hierarchy[label]
                options = [{'id': opt, 'text': opt, 'pre-ann-category': eg['pre-ann-category']}
                           for opt in sub_labels]
                # create new example with text and sub labels as options
                shuffle(options)  # shuffle sub_labels for each example
                new_eg = {'text': eg['text'], 'options': options}
                yield new_eg


@prodigy.recipe(
    "textcat-modified",
    dataset=("The dataset to use", "positional", None, str),
    source=("The name of the source dataset stored as database",
            "positional", None, str),
    # label=("One or more comma-separated labels", "option", "l", split_string),
    exclusive=("Treat classes as mutually exclusive", "flag", "E", bool),
    exclude=("Names of datasets to exclude", "option", "e", split_string),
)
def textcat_modified(  # from https://github.com/explosion/prodigy-recipes/blob/master/textcat/textcat_manual.py
    dataset: str,
    source: str,
    # label: Optional[List[str]] = None,
    exclusive: bool = False,
    exclude: Optional[List[str]] = None,
):
    """
    Manually annotate categories that apply to a text. If more than one label
    is specified, categories are added as multiple choice options. If the
    --exclusive flag is set, categories become mutually exclusive, meaning that
    only one can be selected during annotation.
    """

    # Load the stream directly from a database and return a generator that yields a
    # dictionary for each example in the data.
    db = connect()
    stream = db.get_dataset(source)

    has_options = True
    new_stream = get_stream(stream)

    return {
        # Annotation interface to use
        "view_id": "blocks",
        "dataset": dataset,  # Name of dataset to save annotations
        "stream": new_stream,  # Incoming stream of examples
        "exclude": exclude,  # List of dataset names to exclude
        "config": {  # Additional config settings, mostly for app UI
            "choice_style": "single" if exclusive else "multiple",  # Style of choice interface
            # Hash value used to filter out already seen examples
            "exclude_by": "input" if has_options else "task",
            "blocks": [{"view_id": "choice"},
                       {"view_id": "text_input"}],
        },
    }
