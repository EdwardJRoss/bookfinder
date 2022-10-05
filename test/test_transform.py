from graphlib import CycleError  # type: ignore

import pandas as pd
from hypothesis import assume, given
from hypothesis import strategies as st

from bookfinder.transform import clean_text, enrich_root, get_root_mapping, hash_bucket


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


def test_enrich_root():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "parent": pd.Series([2, 3, 3, 5, None], dtype="Int64"),
        }
    ).set_index("id")
    df_out = enrich_root(df)
    assert df_out["root"].tolist() == [3, 3, 3, 5, 5]


def test_enrich_root_pure():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "parent": [2, 3, 3, 5, 5],
        }
    ).set_index("id")
    _ = enrich_root(df)
    assert "root" not in df.columns


@given(st.floats(allow_nan=False))
def test_hash_bucket(s):
    hash_bucket(s)


def test_clean_text():
    text = (
        "<i>&gt; they’re the only ones who can use FLOC</i>"
        "<p>It is available to everyone:"
        "<p><pre><code>"
        "    cohort = await document.interestCohort();\n"
        "</code></pre>\n"
        'See <a href="https:&#x2F;&#x2F;github.com&#x2F;WICG&#x2F;floc" rel="nofollow">https:&#x2F;&#x2F;github.com&#x2F;WICG&#x2F;floc</a>'
        "<p>(Disclosure: I work for Google, speaking only for myself)"
    )
    clean = clean_text(text)

    assert (
        clean
        == """> they’re the only ones who can use FLOC

It is available to everyone:

    cohort = await document.interestCohort();

See https://github.com/WICG/floc

(Disclosure: I work for Google, speaking only for myself)"""
    )
