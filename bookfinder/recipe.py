import prodigy  # type: ignore
from prodigy.components.loaders import JSONL  # type: ignore
from prodigy.models.ner import EntityRecognizer  # type: ignore
from prodigy.components.preprocess import split_sentences  # type: ignore
from prodigy.util import split_string  # type: ignore
import spacy
from typing import List, Optional, Iterable, Dict, Tuple


def filter_has_ner(stream_predictions: Iterable[Tuple[float, Dict]]) -> Iterable[Dict]:
    for score, prediction in stream_predictions:
        if len(prediction["spans"]) > 0:
            yield prediction


@prodigy.recipe(
    "ner.precise",
    dataset=("The dataset to use", "positional", None, str),
    spacy_model=("The base model", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
    label=("One or more comma-separated labels", "option", "l", split_string),
    exclude=("Names of datasets to exclude", "option", "e", split_string),
    unsegmented=("Don't split sentences", "flag", "U", bool),
)
def ner_precise(
    dataset: str,
    spacy_model: str,
    source: str,
    label: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    unsegmented: bool = False,
):
    stream = JSONL(source)

    nlp = spacy.load(spacy_model)

    model = EntityRecognizer(nlp, label=label)

    if not unsegmented:
        stream = split_sentences(nlp, stream)

    stream = filter_has_ner(model(stream))

    return {
        "view_id": "ner",  # Annotation interface to use
        "dataset": dataset,  # Name of dataset to save annotations
        "stream": stream,  # Incoming stream of examples
        "update": model.update,  # Update callback, called with batch of answers
        "exclude": exclude,  # List of dataset names to exclude
        "config": {"lang": nlp.lang},  # Additional config settings, mostly for app UI
    }
