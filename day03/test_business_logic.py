"""pytest tests for business_logic functions in day03."""

from business_logic import parse_amount, normalize_unit, convert_to_grams, convert_from_grams


def test_parse_amount_integer():
    assert parse_amount("100") == 100.0


def test_parse_amount_fraction():
    assert abs(parse_amount("1/2") - 0.5) < 1e-9


def test_normalize_unit():
    assert normalize_unit("g") == "g"
    assert normalize_unit("grams") == "g"
    assert normalize_unit("Tbsp") == "tbsp"


def test_convert_to_from_grams():
    # Use 200 g per cup (sugar) as example
    gpc = 200.0
    grams = convert_to_grams(1, "cup", gpc)
    assert grams == 200.0
    conv = convert_from_grams(400.0, gpc)
    # 400 g is 2 cups
    assert abs(conv["cup"] - 2.0) < 1e-9
    assert abs(conv["tbsp"] - 32.0) < 1e-9