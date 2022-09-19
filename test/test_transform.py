from graphlib import CycleError

from hypothesis import assume, given
from hypothesis import strategies as st

from bookfinder.transform import get_root_mapping


def test_get_root_mapping():
    parent_dict = {1: 2, 2: 3, 4: 5}
    root_dict = get_root_mapping(parent_dict)
    assert root_dict == {1: 3, 2: 3, 3: 3, 4: 5, 5: 5}


def test_get_root_mapping_empty():
    parent_dict = {}
    root_dict = get_root_mapping(parent_dict)
    assert root_dict == {}


@given(st.dictionaries(st.integers(), st.integers()))
def test_get_root_mapping_idempotent(parent_dict):
    try:
        root_dict = get_root_mapping(parent_dict)
    except CycleError:
        # Exclude graphs with cycles
        assume(False)
    assert root_dict == get_root_mapping(root_dict)


@given(st.dictionaries(st.integers(), st.integers()))
def test_get_root_mapping_parent_root(parent_dict):
    try:
        root_dict = get_root_mapping(parent_dict)
    except CycleError:
        # Exclude graphs with cycles
        assume(False)
    for child, parent in parent_dict.items():
        assert root_dict[child] == root_dict[parent]
