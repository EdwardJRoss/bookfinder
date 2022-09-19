from bookfinder.transform import get_root_mapping


def test_get_root_mapping():
    parent_dict = {1: 2, 2: 3, 4: 5}
    root_dict = get_root_mapping(parent_dict)
    assert root_dict == {1: 3, 2: 3, 4: 5}
