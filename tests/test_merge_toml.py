import pytest
from deepdiff import DeepDiff

from bhtmeter.utils.merge_toml import merge_toml

def assertEquals(d1, d2) -> None:
    assert len(DeepDiff(d1, d2)) == 0

class TestMergeToml:
    def test_empty(self):
        r = merge_toml({}, {})
        assert len(r) == 0
        r1 = merge_toml({'k1': 'v1'}, {})
        assertEquals({'k1': 'v1'}, r1)
        r2 = merge_toml({}, {'k1': 'v1'})
        assertEquals({'k1': 'v1'}, r2)
        
    def test_disjoint(self):
        r = merge_toml({'k1':'v1'}, {'k2':'v2'})
        assertEquals({'k1':'v1', 'k2':'v2'}, r)

    def test_samekey_diffitem(self):
        r = merge_toml({'k1':'v1'}, {'k1':'v2'})
        assertEquals({'k1':['v1', 'v2']}, r)

    def test_samekey_sameitem(self):
        r = merge_toml({'k1':'v1'}, {'k1':'v1'})
        assertEquals({'k1':'v1'}, r)
        r = merge_toml({'k1':123}, {'k1':123})
        assertEquals({'k1':123}, r)

    def test_samekey_list(self):
        r = merge_toml({'k1':['v11', 'v12']}, {'k1':'v2'})
        assertEquals({'k1':['v11', 'v12', 'v2']}, r)
        r = merge_toml({'k1':'v1'}, {'k1':['v21', 'v22']})
        assertEquals({'k1':['v1', 'v21', 'v22']}, r)

    def test_samekey_empty(self):
        r = merge_toml({'k1': {'k11':'v11'}}, {})
        assertEquals({'k1': {'k11':'v11'}}, r)
        r = merge_toml({}, {'k2': {'k21':'v21'}})
        assertEquals({'k2': {'k21':'v21'}}, r)

    def test_samekey_table(self):
        r = merge_toml({'k1': {'k11':'v11'}}, {'k1': {'k21': 'v21'}})
        assertEquals({'k1': {'k11':'v11', 'k21':'v21'}}, r)
        r = merge_toml({'k1': {'k11':'v11'}}, {'k1': {'k11': 'v21'}})
        assertEquals({'k1': {'k11':['v11','v21']}}, r)
