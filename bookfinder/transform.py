from typing import TypeVar

T = TypeVar("T")


def get_root_mapping(parent_dict: dict[T, T]) -> dict[T, T]:
    """Return a mapping of each node to its root node."""
    root_dict = {}

    for item, parent in parent_dict.items():
        while parent in parent_dict:
            grandparent = parent_dict[parent]
            if parent == grandparent:
                break
            parent = grandparent
        root_dict[item] = parent

    return root_dict
