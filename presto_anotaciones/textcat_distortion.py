import prodigy
from prodigy.components.loaders import get_stream
from typing import List, Optional, Union, Iterable
from typing import List, Optional
from functools import reduce
from prodigy.util import split_string
from random import shuffle
from prodigy.util import log, msg, get_labels, split_string, INPUT_HASH_ATTR
from prodigy.components.preprocess import add_label_options, add_labels_to_stream
from prodigy.components.db import connect

hierarchy = {'distorsión': ['sobregeneralización', 'leer la mente', 'imperativos', 'etiquetado',
                            'pensamiento absolutista', 'adivinación', 'catastrofismo', 'abstracción selectiva',
                            'razonamiento emocional', 'personalización'], 'no distorsión': []}


# Recipe for hierarchical multi-label text classification with comment box intereface.
# Slightly modified from the source code: prodigy/recipes/textcat.py
@prodigy.recipe(
    "textcat.hierarchical_multiple",
    # fmt: off
    dataset=("Dataset to save annotations to", "positional", None, str),
    source=("Data to annotate (file path or '-' to read from standard input)", "positional", None, str),
    loader=("Loader (guessed from file extension if not set)", "option", "lo", str),
    label=("Comma-separated label(s) to annotate or text file with one label per line", "option", "l", get_labels),
    exclusive=(
            "Treat classes as mutually exclusive (if not set, an example can have multiple correct classes)", "flag",
            "E",
            bool),
    exclude=("Comma-separated list of dataset IDs whose annotations to exclude", "option", "e", split_string),
    # fmt: on
)
def textcat_hierarchical_multiple(
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
            if dataset in db:
                stream = filter_accepted_inputs(
                    db.get_dataset(dataset), stream)

    distortion_options = hierarchy.get('distorsión')
    distortion_options_html = reduce(lambda accumulator,
                                            current: accumulator + f'<label for="{current}" class="prodigy-option c0198" data-prodigy-option="{current}"><input class="c01100 distortion-option" name="{current}" type="checkbox" id="{current}"><a class="c01101"><div class="prodigy-content c0190 c0189">{current}</div></a></label>',
                                     distortion_options, '')
    html_template = f'<div tabindex="-1"><div class="prodigy-options c0178" id="distortion-type-options">{distortion_options_html}</div></div> '
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": stream,
        "exclude": exclude,
        "config": {
            "labels": labels,
            "choice_style": "single",
            # "choice_auto_accept": exclusive,
            "exclude_by": "input" if has_options else "task",
            "auto_count_stream": True,
            "blocks": [{"view_id": "choice"},
                       {"view_id": "text_input"},
                       {"view_id": "html", "html_template": html_template}]
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
