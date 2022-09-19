from graphlib import TopologicalSorter
from typing import TypeVar

import xxhash  # type: ignore
from beartype import beartype

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


@beartype
def hash_bucket(s: float, salt: str = "hnbooks") -> int:
    """Return a deterministic hash bucket in 0-99.

    Use a float for consistency with the original splitting.
    """
    bucket = xxhash.xxh32_intdigest(str(s) + salt) % 100
    assert 0 <= bucket < 100
    return bucket
