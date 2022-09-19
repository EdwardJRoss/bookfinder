from graphlib import TopologicalSorter
from typing import TypeVar

T = TypeVar("T")


def get_root_mapping(parent_dict: dict[T, T]) -> dict[T, T]:
    """Return a mapping of each node to its root node."""
    root_dict = {}
    for node in TopologicalSorter(
        {k: [v] for k, v in parent_dict.items()}
    ).static_order():
        if node not in parent_dict:
            root_dict[node] = node
        else:
            root_dict[node] = root_dict[parent_dict[node]]
    return root_dict
