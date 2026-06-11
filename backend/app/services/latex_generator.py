from typing import Dict, Any, Callable, Optional

class LatexGenerator:
    """
    Extensible LaTeX Generation Service.
    
    Translates a Mathematical Expression AST (as serialized dict) into valid LaTeX.
    Uses a dispatch registry to easily allow adding or modifying handlers.
    """
    
    def __init__(self) -> None:
        # Default handler registry mapping node types to generation functions
        self._handlers: Dict[str, Callable[[Dict[str, Any]], str]] = {
            "number": self._handle_number,
            "variable": self._handle_variable,
            "operator": self._handle_operator,
            "superscript": self._handle_superscript,
            "subscript": self._handle_subscript,
            "fraction": self._handle_fraction,
            "sqrt": self._handle_sqrt,
            "group": self._handle_group,
            "integral": self._handle_integral,
            "summation": self._handle_summation,
            "limit": self._handle_limit,
            "matrix": self._handle_matrix,
            "empty": self._handle_empty
        }

    def register_handler(self, node_type: str, handler_fn: Callable[[Dict[str, Any]], str]) -> None:
        """
        Registers a custom handler function for a specific AST node type,
        enabling easy extensibility of the parser layout engine.
        """
        self._handlers[node_type] = handler_fn

    def generate(self, ast: Optional[Dict[str, Any]]) -> str:
        """
        Translates a serialized AST node dictionary recursively into LaTeX.
        """
        if not ast:
            return ""
            
        node_type = ast.get("type")
        handler = self._handlers.get(node_type)
        if not handler:
            raise ValueError(f"No LaTeX generation handler registered for node type '{node_type}'")
            
        return handler(ast)

    def _handle_number(self, node: Dict[str, Any]) -> str:
        return str(node.get("value", ""))

    def _handle_variable(self, node: Dict[str, Any]) -> str:
        val = node.get("value", "")
        # Map constants and symbols to LaTeX equivalents
        mapping = {
            "pi": r"\pi",
            "inf": r"\infty",
            "theta": r"\theta",
            "alpha": r"\alpha",
            "beta": r"\beta",
            "gamma": r"\gamma"
        }
        return mapping.get(val, str(val))

    def _handle_operator(self, node: Dict[str, Any]) -> str:
        val = node.get("value", "")
        left_node = node.get("left")
        right_node = node.get("right")
        
        # Standard operator replacements
        mapping = {
            "leq": r"\le",
            "geq": r"\ge",
            "neq": r"\ne"
        }
        latex_op = mapping.get(val, val)
        
        # Handle binary operation formatting
        if left_node is not None or right_node is not None:
            left_str = self.generate(left_node)
            right_str = self.generate(right_node)
            
            # Special case: Multiplication
            if val == "*":
                # If both operands are numbers, use explicit multiplication dot \cdot
                if self._is_numeric_node(left_node) and self._is_numeric_node(right_node):
                    return f"{left_str}\\cdot {right_str}"
                # Otherwise, use standard algebraic juxtaposition (implicit multiplication)
                return f"{left_str}{right_str}"
                
            # Formatting for unary operator (left operand is missing)
            if left_node is None:
                return f"{latex_op}{right_str}"
                
            return f"{left_str}{latex_op}{right_str}"
            
        return str(latex_op)

    def _handle_superscript(self, node: Dict[str, Any]) -> str:
        base_str = self.generate(node.get("base"))
        exponent_str = self.generate(node.get("exponent"))
        # Use brackets for multi-character exponents, or always for safety
        if len(exponent_str) == 1:
            return f"{base_str}^{exponent_str}"
        return f"{base_str}^{{{exponent_str}}}"

    def _handle_subscript(self, node: Dict[str, Any]) -> str:
        base_str = self.generate(node.get("base"))
        sub_str = self.generate(node.get("sub"))
        if len(sub_str) == 1:
            return f"{base_str}_{sub_str}"
        return f"{base_str}_{{{sub_str}}}"

    def _handle_fraction(self, node: Dict[str, Any]) -> str:
        num_str = self.generate(node.get("numerator"))
        den_str = self.generate(node.get("denominator"))
        return f"\\frac{{{num_str}}}{{{den_str}}}"

    def _handle_sqrt(self, node: Dict[str, Any]) -> str:
        radicand_str = self.generate(node.get("radicand"))
        return f"\\sqrt{{{radicand_str}}}"

    def _handle_group(self, node: Dict[str, Any]) -> str:
        expr_str = self.generate(node.get("expression"))
        bracket_char = node.get("value", "(")
        
        # Enclose with proper scaling bracket size commands
        bracket_pairs = {
            "(": (r"\left(", r"\right)"),
            "[": (r"\left[", r"\right]"),
            "{": (r"\left\{", r"\right\}")
        }
        open_b, close_b = bracket_pairs.get(bracket_char, (r"\left(", r"\right)"))
        return f"{open_b}{expr_str}{close_b}"

    def _handle_integral(self, node: Dict[str, Any]) -> str:
        lower = self.generate(node.get("lower_limit"))
        upper = self.generate(node.get("upper_limit"))
        expr = self.generate(node.get("expression"))
        
        limit_str = ""
        if lower:
            limit_str += f"_{{{lower}}}"
        if upper:
            limit_str += f"^{{{upper}}}"
            
        sep = " " if expr else ""
        return f"\\int{limit_str}{sep}{expr}"

    def _handle_summation(self, node: Dict[str, Any]) -> str:
        lower = self.generate(node.get("lower_limit"))
        upper = self.generate(node.get("upper_limit"))
        expr = self.generate(node.get("expression"))
        
        limit_str = ""
        if lower:
            limit_str += f"_{{{lower}}}"
        if upper:
            limit_str += f"^{{{upper}}}"
            
        sep = " " if expr else ""
        return f"\\sum{limit_str}{sep}{expr}"

    def _handle_limit(self, node: Dict[str, Any]) -> str:
        lower = self.generate(node.get("lower_limit"))
        expr = self.generate(node.get("expression"))
        
        limit_str = ""
        if lower:
            limit_str += f"_{{{lower}}}"
            
        sep = " " if expr else ""
        return f"\\lim{limit_str}{sep}{expr}"

    def _handle_matrix(self, node: Dict[str, Any]) -> str:
        rows = node.get("rows", [])
        bracket_char = node.get("value", "[")
        
        # Determine matrix latex environment
        matrix_envs = {
            "[": "bmatrix",
            "(": "pmatrix",
            "{": "Bmatrix"
        }
        env = matrix_envs.get(bracket_char, "matrix")
        
        formatted_rows = []
        for row in rows:
            formatted_cells = [self.generate(cell) for cell in row]
            formatted_rows.append(" & ".join(formatted_cells))
            
        rows_str = " \\\\ ".join(formatted_rows)
        return f"\\begin{{{env}}}{rows_str}\\end{{{env}}}"

    def _handle_empty(self, node: Dict[str, Any]) -> str:
        return ""

    def _is_numeric_node(self, node: Optional[Dict[str, Any]]) -> bool:
        if not node:
            return False
        if node.get("type") == "number":
            return True
        # Recursively check operator nodes
        if node.get("type") == "operator":
            val = node.get("value")
            # If it's a number operation, it might end up numeric
            return val in ("*", "+", "-") and self._is_numeric_node(node.get("left")) and self._is_numeric_node(node.get("right"))
        return False
