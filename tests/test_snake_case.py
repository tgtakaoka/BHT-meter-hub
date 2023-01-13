import pytest

from bhtmeter.utils.snake_case import snake_case


class TestSnakeCase:
    def test_no_upper(self):
        text = snake_case("abc")
        assert text == "abc"

    def test_all_upper(self):
        text = snake_case("ABC")
        assert text == "abc"

    def test_starts_with_lower(self):
        text = snake_case("abcXyz")
        assert text == "abc_xyz"

    def test_starts_with_upper(self):
        text = snake_case("AbcXyz")
        assert text == "abc_xyz"

    def test_starts_with_allcaps(self):
        text = snake_case("ABCXyz")
        assert text == "abc_xyz"

    def test_end_with_allcaps(self):
        text = snake_case("AbcXYZ")
        assert text == "abc_xyz"

    def test_contains_allcaps(self):
        text = snake_case("AbcXYZPqr")
        assert text == "abc_xyz_pqr"

    def test_already_snakecase(self):
        text = snake_case("abc_def_012")
        assert text == "abc_def_012"

    def test_to_upper(self):
        text = snake_case("AbcXYZPqr", upper=True)
        assert text == "ABC_XYZ_PQR"
