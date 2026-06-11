import pytest
from app.services.expression_parser import ExpressionParser

@pytest.fixture
def parser():
    return ExpressionParser()

def test_simple_expression(parser):
    # Expression: x + y
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 120, 130]},
        {"symbol": "+", "bbox": [140, 110, 155, 125]},
        {"symbol": "y", "bbox": [175, 100, 195, 130]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "operator"
    assert ast["value"] == "+"
    assert ast["left"]["type"] == "variable"
    assert ast["left"]["value"] == "x"
    assert ast["right"]["type"] == "variable"
    assert ast["right"]["value"] == "y"

def test_superscript(parser):
    # Expression: x^2 (as in user request example)
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 130, 140]},
        {"symbol": "2", "bbox": [135, 70, 155, 95]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "superscript"
    assert ast["base"]["type"] == "variable"
    assert ast["base"]["value"] == "x"
    assert ast["exponent"]["type"] == "number"
    assert ast["exponent"]["value"] == "2"

def test_subscript(parser):
    # Expression: x_i
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 130, 140]},
        {"symbol": "i", "bbox": [135, 135, 145, 155]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "subscript"
    assert ast["base"]["type"] == "variable"
    assert ast["base"]["value"] == "x"
    assert ast["sub"]["type"] == "variable"
    assert ast["sub"]["value"] == "i"

def test_fraction(parser):
    # Expression: a / b
    symbols = [
        {"symbol": "a", "bbox": [110, 50, 130, 80]},
        {"symbol": "-", "bbox": [100, 90, 140, 95]}, # fraction bar
        {"symbol": "b", "bbox": [110, 105, 130, 135]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "fraction"
    assert ast["numerator"]["type"] == "variable"
    assert ast["numerator"]["value"] == "a"
    assert ast["denominator"]["type"] == "variable"
    assert ast["denominator"]["value"] == "b"

def test_square_root(parser):
    # Expression: sqrt(x)
    symbols = [
        {"symbol": "sqrt", "bbox": [100, 80, 150, 140]},
        {"symbol": "x", "bbox": [115, 100, 135, 130]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "sqrt"
    assert ast["radicand"]["type"] == "variable"
    assert ast["radicand"]["value"] == "x"

def test_nested_roots(parser):
    # Expression: sqrt(sqrt(x))
    symbols = [
        {"symbol": "sqrt", "bbox": [100, 70, 200, 150]}, # Outer sqrt
        {"symbol": "sqrt", "bbox": [115, 90, 180, 140]}, # Inner sqrt
        {"symbol": "x", "bbox": [135, 105, 155, 130]}     # Inner variable
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "sqrt"
    assert ast["radicand"]["type"] == "sqrt"
    assert ast["radicand"]["radicand"]["type"] == "variable"
    assert ast["radicand"]["radicand"]["value"] == "x"

def test_parentheses_groups(parser):
    # Expression: (x + y)
    symbols = [
        {"symbol": "(", "bbox": [100, 80, 110, 140]},
        {"symbol": "x", "bbox": [120, 100, 135, 130]},
        {"symbol": "+", "bbox": [145, 110, 155, 120]},
        {"symbol": "y", "bbox": [165, 100, 180, 130]},
        {"symbol": ")", "bbox": [190, 80, 200, 140]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "group"
    assert ast["expression"]["type"] == "operator"
    assert ast["expression"]["value"] == "+"

def test_limits_integrals_summations(parser):
    # Expression: int_{a}^{b} x
    symbols = [
        {"symbol": "int", "bbox": [100, 80, 115, 160]},
        {"symbol": "a", "bbox": [110, 170, 120, 190]}, # subscript / lower limit
        {"symbol": "b", "bbox": [110, 50, 120, 70]},   # superscript / upper limit
        {"symbol": "x", "bbox": [130, 110, 145, 135]}   # body expression
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "integral"
    assert ast["lower_limit"]["type"] == "variable"
    assert ast["lower_limit"]["value"] == "a"
    assert ast["upper_limit"]["type"] == "variable"
    assert ast["upper_limit"]["value"] == "b"
    assert ast["expression"]["type"] == "variable"
    assert ast["expression"]["value"] == "x"

def test_matrix(parser):
    # Expression: 2x2 matrix
    symbols = [
        {"symbol": "[", "bbox": [100, 80, 110, 200]},
        # Row 1
        {"symbol": "1", "bbox": [120, 100, 130, 120]},
        {"symbol": "2", "bbox": [150, 100, 160, 120]},
        # Row 2
        {"symbol": "3", "bbox": [120, 150, 130, 170]},
        {"symbol": "4", "bbox": [150, 150, 160, 170]},
        {"symbol": "]", "bbox": [180, 80, 190, 200]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "matrix"
    assert len(ast["rows"]) == 2
    assert len(ast["rows"][0]) == 2
    assert len(ast["rows"][1]) == 2
    assert ast["rows"][0][0]["type"] == "number"
    assert ast["rows"][0][0]["value"] == "1"
    assert ast["rows"][0][1]["type"] == "number"
    assert ast["rows"][0][1]["value"] == "2"
    assert ast["rows"][1][0]["type"] == "number"
    assert ast["rows"][1][0]["value"] == "3"
    assert ast["rows"][1][1]["type"] == "number"
    assert ast["rows"][1][1]["value"] == "4"

def test_complex_expression(parser):
    # Expression: x^2 + (y / z)
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 120, 130]},
        {"symbol": "2", "bbox": [125, 75, 140, 95]},
        {"symbol": "+", "bbox": [150, 105, 165, 120]},
        {"symbol": "(", "bbox": [175, 80, 185, 150]},
        {"symbol": "y", "bbox": [200, 90, 215, 105]},
        {"symbol": "-", "bbox": [195, 115, 220, 120]}, # fraction bar
        {"symbol": "z", "bbox": [200, 130, 215, 145]},
        {"symbol": ")", "bbox": [230, 80, 240, 150]}
    ]
    
    ast = parser.parse(symbols)
    assert ast is not None
    assert ast["type"] == "operator"
    assert ast["value"] == "+"
    assert ast["left"]["type"] == "superscript"
    assert ast["right"]["type"] == "group"
    assert ast["right"]["expression"]["type"] == "fraction"
