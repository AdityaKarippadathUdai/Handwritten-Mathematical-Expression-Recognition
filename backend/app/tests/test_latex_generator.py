import pytest
from app.services.expression_parser import ExpressionParser
from app.services.latex_generator import LatexGenerator

@pytest.fixture
def parser():
    return ExpressionParser()

@pytest.fixture
def generator():
    return LatexGenerator()

def test_simple_latex(parser, generator):
    # Expression: x + y
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 120, 130]},
        {"symbol": "+", "bbox": [140, 110, 155, 125]},
        {"symbol": "y", "bbox": [175, 100, 195, 130]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == "x+y"

def test_superscript_latex(parser, generator):
    # Expression: x^2
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 130, 140]},
        {"symbol": "2", "bbox": [135, 70, 155, 95]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == "x^2"

def test_subscript_latex(parser, generator):
    # Expression: x_i
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 130, 140]},
        {"symbol": "i", "bbox": [135, 135, 145, 155]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == "x_i"

def test_fraction_latex(parser, generator):
    # Expression: a / b
    symbols = [
        {"symbol": "a", "bbox": [110, 50, 130, 80]},
        {"symbol": "-", "bbox": [100, 90, 140, 95]},
        {"symbol": "b", "bbox": [110, 105, 130, 135]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"\frac{a}{b}"

def test_square_root_latex(parser, generator):
    # Expression: sqrt(x)
    symbols = [
        {"symbol": "sqrt", "bbox": [100, 80, 150, 140]},
        {"symbol": "x", "bbox": [115, 100, 135, 130]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"\sqrt{x}"

def test_nested_roots_latex(parser, generator):
    # Expression: sqrt(sqrt(x))
    symbols = [
        {"symbol": "sqrt", "bbox": [100, 70, 200, 150]},
        {"symbol": "sqrt", "bbox": [115, 90, 180, 140]},
        {"symbol": "x", "bbox": [135, 105, 155, 130]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"\sqrt{\sqrt{x}}"

def test_parentheses_groups_latex(parser, generator):
    # Expression: (x + y)
    symbols = [
        {"symbol": "(", "bbox": [100, 80, 110, 140]},
        {"symbol": "x", "bbox": [120, 100, 135, 130]},
        {"symbol": "+", "bbox": [145, 110, 155, 120]},
        {"symbol": "y", "bbox": [165, 100, 180, 130]},
        {"symbol": ")", "bbox": [190, 80, 200, 140]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"\left(x+y\right)"

def test_limits_integrals_summations_latex(parser, generator):
    # Expression: int_{a}^{b} x
    symbols = [
        {"symbol": "int", "bbox": [100, 80, 115, 160]},
        {"symbol": "a", "bbox": [110, 170, 120, 190]},
        {"symbol": "b", "bbox": [110, 50, 120, 70]},
        {"symbol": "x", "bbox": [130, 110, 145, 135]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"\int_{a}^{b} x"

def test_matrix_latex(parser, generator):
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
    latex = generator.generate(ast)
    assert latex == r"\begin{bmatrix}1 & 2 \\ 3 & 4\end{bmatrix}"

def test_complex_expression_latex(parser, generator):
    # Expression: x^2 + (y / z)
    symbols = [
        {"symbol": "x", "bbox": [100, 100, 120, 130]},
        {"symbol": "2", "bbox": [125, 75, 140, 95]},
        {"symbol": "+", "bbox": [150, 105, 165, 120]},
        {"symbol": "(", "bbox": [175, 80, 185, 150]},
        {"symbol": "y", "bbox": [200, 90, 215, 105]},
        {"symbol": "-", "bbox": [195, 115, 220, 120]},
        {"symbol": "z", "bbox": [200, 130, 215, 145]},
        {"symbol": ")", "bbox": [230, 80, 240, 150]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"x^2+\left(\frac{y}{z}\right)"

def test_constants_latex(parser, generator):
    # Expression: pi + inf
    symbols = [
        {"symbol": "pi", "bbox": [100, 100, 120, 130]},
        {"symbol": "+", "bbox": [130, 110, 140, 120]},
        {"symbol": "inf", "bbox": [150, 100, 170, 130]}
    ]
    ast = parser.parse(symbols)
    latex = generator.generate(ast)
    assert latex == r"\pi+\infty"

def test_implicit_multiplication_latex(parser, generator):
    # Expression: 2 * 3 (explicit) -> 2 \cdot 3
    # Expression: 2 * x (implicit) -> 2x
    # Explicit 2*3
    symbols_explicit = [
        {"symbol": "2", "bbox": [100, 100, 110, 120]},
        {"symbol": "*", "bbox": [120, 105, 130, 115]},
        {"symbol": "3", "bbox": [140, 100, 150, 120]}
    ]
    ast_explicit = parser.parse(symbols_explicit)
    latex_explicit = generator.generate(ast_explicit)
    assert latex_explicit == r"2\cdot 3"

    # Implicit 2x
    symbols_implicit = [
        {"symbol": "2", "bbox": [100, 100, 115, 120]},
        {"symbol": "x", "bbox": [125, 100, 140, 120]}
    ]
    ast_implicit = parser.parse(symbols_implicit)
    latex_implicit = generator.generate(ast_implicit)
    assert latex_implicit == "2x"

def test_extensibility(generator):
    # Register custom handler
    generator.register_handler("custom_type", lambda node: f"\\custom{{{node.get('value')}}}")
    
    ast = {
        "type": "custom_type",
        "value": "hello"
    }
    latex = generator.generate(ast)
    assert latex == r"\custom{hello}"
