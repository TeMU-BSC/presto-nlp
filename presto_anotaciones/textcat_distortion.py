import prodigy
from prodigy.components.loaders import get_stream
from typing import List, Optional, Union, Iterable
from typing import List, Optional
from prodigy.util import split_string
from random import shuffle
from prodigy.util import log, msg, get_labels, split_string, INPUT_HASH_ATTR
from prodigy.components.preprocess import add_label_options, add_labels_to_stream
from prodigy.components.db import connect

hierarchy = {'distorsión': ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                            'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                            'razonamiento emocional', 'personalización'], 'no distorsión': []}

# from https://support.prodi.gy/t/does-prodigy-supports-hierarchical-annotation/1249/9

# Custom streamer


def get_stream_nested(examples):
    for eg in examples:   # the examples with top-level categories
        top_labels = eg['accept']  # ['A'] or ['B', 'C'] if multiple choice
        for label in top_labels:
            if label != "no distorsión":
                sub_labels = hierarchy[label]
                options = [{'id': opt, 'text': opt, 'pre-ann-category': eg['pre-ann-category']}
                           for opt in sub_labels]
                # create new example with text and sub labels as options
                shuffle(options)  # shuffle sub_labels for each example
                new_eg = {'id': eg['id'],'text': eg['text'], 'options': options,
                          'pre-ann-category': eg['pre-ann-category']}
                yield new_eg


@prodigy.recipe(
    "textcat.multiple_nested",
    dataset=("The dataset to use", "positional", None, str),
    source=("The name of the source dataset stored as database",
            "positional", None, str),
    # label=("One or more comma-separated labels", "option", "l", split_string),
    exclusive=("Treat classes as mutually exclusive", "flag", "E", bool),
    exclude=("Names of datasets to exclude", "option", "e", split_string),
)
def textcat_multiple_nested(  # from https://github.com/explosion/prodigy-recipes/blob/master/textcat/textcat_manual.py
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
    new_stream = get_stream_nested(stream)

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


# Recipe for standard text classification with comment box intereface.
# Slightly modified from the source code: prodigy/recipes/textcat.py
@prodigy.recipe(
    "textcat.choice_with_comment",
    # fmt: off
    dataset=("Dataset to save annotations to", "positional", None, str),
    source=("Data to annotate (file path or '-' to read from standard input)", "positional", None, str),
    loader=("Loader (guessed from file extension if not set)", "option", "lo", str),
    label=("Comma-separated label(s) to annotate or text file with one label per line", "option", "l", get_labels),
    exclusive=("Treat classes as mutually exclusive (if not set, an example can have multiple correct classes)", "flag", "E", bool),
    exclude=("Comma-separated list of dataset IDs whose annotations to exclude", "option", "e", split_string),
    # fmt: on
)
def textcat_choice_with_comment(
    dataset: str,
    source: Union[str, Iterable[dict]],
    loader: Optional[str] = None,
    label: Optional[List[str]] = None,
    exclusive: bool = False,
    exclude: Optional[List[str]] = None,
):
    """
    Manually annotate categories that apply to a text. If more than one label
    is specified, categories are added as multiple choice options. If the
    --exclusive flag is set, categories become mutually exclusive, meaning that
    only one can be selected during annotation.
    """
    log("RECIPE: Starting recipe textcat.manual", locals())
    labels = label
    if not labels:
        msg.fail("textcat.manual requires at least one --label", exits=1)
    has_options = len(labels) > 1
    log(f"RECIPE: Annotating with {len(labels)} labels", labels)
    stream = get_stream(
        source, loader=loader, rehash=True, dedup=True, input_key="text"
    )
    if has_options:
        stream = add_label_options(stream, label)
    else:
        stream = add_labels_to_stream(stream, label)
        if exclusive:
            # Use the dataset to decide what's left to annotate
            db = connect()
            import pdb
            pdb.set_trace()
            if dataset in db:
                stream = filter_accepted_inputs(
                    db.get_dataset(dataset), stream)
                import pdb
                pdb.set_trace()

    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": stream,
        "exclude": exclude,
        "config": {
            "labels": labels,
            "choice_style": "single" if exclusive else "multiple",
            "choice_auto_accept": exclusive,
            "exclude_by": "input" if has_options else "task",
            "auto_count_stream": True,
            "blocks": [{"view_id": "choice"},
                       {"view_id": "text_input"}]
        },
    }


def filter_accepted_inputs(examples, stream):
    # If a single label is annotated with --exclusive, we only want to show
    # examples that aren't yet in the dataset or examples that were not yet
    # accepted (i.e. that we don't yet know the answer for).
    accepted = set()
    for eg in examples:
        if eg["answer"] == "accept":
            accepted.add(eg[INPUT_HASH_ATTR])
    for eg in stream:
        if eg[INPUT_HASH_ATTR] not in accepted:
            yield eg
