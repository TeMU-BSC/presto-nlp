import prodigy
from prodigy.components.loaders import JSONL
from typing import List, Optional
from prodigy.util import split_string

hierarchy = {'yes': ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                     'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva'
                     'razonamiento emocional', 'personalización'], 'no': ['no hay distorsión']}

def get_stream(examples): # from https://support.prodi.gy/t/does-prodigy-supports-hierarchical-annotation/1249/9
    for eg in examples:   # the examples with top-level categories
        top_labels = eg['accept']  # ['A'] or ['B', 'C'] if multiple choice
        for label in top_labels:
            sub_labels = hierarchy[label]
            options = [{'id': opt, 'text': opt} for opt in sub_labels]
            # create new example with text and sub labels as options
            new_eg = {'text': eg['text'], 'options': options}
            yield new_eg

# Helper functions for adding user provided labels to annotation tasks.
# def add_label_options_to_stream(stream, labels):
#     options = [{"id": label, "text": label} for label in labels]
#     for task in stream:
#         task["options"] = options
#         yield task
#
# def add_labels_to_stream(stream, labels):
#     for task in stream:
#         task["label"] = labels[0]
#         yield task


@prodigy.recipe(
    "textcat-modified",
    dataset=("The dataset to use", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
    #label=("One or more comma-separated labels", "option", "l", split_string),
    exclusive=("Treat classes as mutually exclusive", "flag", "E", bool),
    exclude=("Names of datasets to exclude", "option", "e", split_string),
)
def textcat_modified( # from https://github.com/explosion/prodigy-recipes/blob/master/textcat/textcat_manual.py
    dataset: str,
    source: str,
    #label: Optional[List[str]] = None,
    exclusive: bool = False,
    exclude: Optional[List[str]] = None,
):
    """
    Manually annotate categories that apply to a text. If more than one label
    is specified, categories are added as multiple choice options. If the
    --exclusive flag is set, categories become mutually exclusive, meaning that
    only one can be selected during annotation.
    """

    # Load the stream from a JSONL file and return a generator that yields a
    # dictionary for each example in the data.
    stream = JSONL(source)

    #Add labels to each task in stream
    # has_options = len(label) > 1
    # if has_options:
    #     stream = add_label_options_to_stream(stream, label)
    # else:
    #     stream = add_labels_to_stream(stream, label)
    #
    # for line in stream:
    #     print(line)

    has_options = True
    new_stream = get_stream(stream)

    return {
        "view_id": "choice" if has_options else "classification",  # Annotation interface to use
        "dataset": dataset,  # Name of dataset to save annotations
        "stream": new_stream,  # Incoming stream of examples
        "exclude": exclude,  # List of dataset names to exclude
        "config": {  # Additional config settings, mostly for app UI
            "choice_style": "single" if exclusive else "multiple", # Style of choice interface
            "exclude_by": "input" if has_options else "task", # Hash value used to filter out already seen examples
        },
    }