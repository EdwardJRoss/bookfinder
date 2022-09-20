import html
import re
from graphlib import TopologicalSorter
from math import isnan
from typing import TypeVar

import pandera as pa
import xxhash  # type: ignore
from beartype import beartype
from pandera.typing import DataFrame, Index, Series

T = TypeVar("T")


def get_root_mapping(parent_dict: dict[T, T]) -> dict[T, T]:
    """Return a mapping of each node to its root node."""
    root_dict = {node: parent for node, parent in parent_dict.items() if node == parent}
    parent_dict = {
        node: parent for node, parent in parent_dict.items() if node != parent
    }
    for node in TopologicalSorter(
        {k: [v] for k, v in parent_dict.items()}
    ).static_order():
        if node not in parent_dict:
            root_dict[node] = node
        else:
            root_dict[node] = root_dict[parent_dict[node]]
    return root_dict


class ParentSchema(pa.SchemaModel):
    id: Index[int]
    parent: Series[int] = pa.Field(nullable=True)


class ParentRootSchema(ParentSchema):
    root: Series[int]


@pa.check_types
def enrich_root(df: DataFrame[ParentSchema]) -> DataFrame[ParentRootSchema]:
    parent_dict = df["parent"].fillna(df.index.to_series()).to_dict()
    root_dict = get_root_mapping(parent_dict)
    return df.assign(root=df.index.map(root_dict)).pipe(DataFrame[ParentRootSchema])


@beartype
def hash_bucket(s: float, salt: str = "hnbooks") -> int:
    """Return a deterministic hash bucket in 0-99.

    Use a float for consistency with the original splitting.
    """
    if isnan(s):
        raise ValueError("NaN is not a valid input")
    bucket = xxhash.xxh32_intdigest(str(s) + salt) % 100
    assert 0 <= bucket < 100
    return bucket


CLEAN_PATTERNS = {
    re.compile("<p>"): "\n\n",
    re.compile("<i>"): r"",
    re.compile("</i>"): r"",
    re.compile('<a href="([^"]*)"[^>]*>.*?</a>'): r"\1",
    re.compile("<pre><code>((?:.|\n)*?)</code></pre>", flags=re.MULTILINE): r"\1",
}


def clean_text(s):
    for match, sub in CLEAN_PATTERNS.items():
        s = match.sub(sub, s)
    return html.unescape(s)
