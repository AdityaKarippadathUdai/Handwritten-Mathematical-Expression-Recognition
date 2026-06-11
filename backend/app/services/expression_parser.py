import os
from typing import List, Dict, Any, Optional

class ASTNode:
    """
    Represents a node in the Abstract Syntax Tree (AST) of a mathematical expression.
    """
    def __init__(
        self,
        type: str,
        value: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        children: Optional[List["ASTNode"]] = None,
        base: Optional["ASTNode"] = None,
        exponent: Optional["ASTNode"] = None,
        sub: Optional["ASTNode"] = None,
        numerator: Optional["ASTNode"] = None,
        denominator: Optional["ASTNode"] = None,
        radicand: Optional["ASTNode"] = None,
        lower_limit: Optional["ASTNode"] = None,
        upper_limit: Optional["ASTNode"] = None,
        expression: Optional["ASTNode"] = None,
        rows: Optional[List[List["ASTNode"]]] = None,
        left: Optional["ASTNode"] = None,
        right: Optional["ASTNode"] = None,
    ):
        self.type = type
        self.value = value
        self.bbox = bbox or []
        self.children = children
        self.base = base
        self.exponent = exponent
        self.sub = sub
        self.numerator = numerator
        self.denominator = denominator
        self.radicand = radicand
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.expression = expression
        self.rows = rows
        self.left = left
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the AST node and its children into a nested dictionary representation.
        """
        result = {"type": self.type}
        if self.value is not None:
            result["value"] = self.value
        if self.bbox:
            result["bbox"] = self.bbox
        if self.children is not None:
            result["children"] = [c.to_dict() for c in self.children]
        if self.base is not None:
            result["base"] = self.base.to_dict()
        if self.exponent is not None:
            result["exponent"] = self.exponent.to_dict()
        if self.sub is not None:
            result["sub"] = self.sub.to_dict()
        if self.numerator is not None:
            result["numerator"] = self.numerator.to_dict()
        if self.denominator is not None:
            result["denominator"] = self.denominator.to_dict()
        if self.radicand is not None:
            result["radicand"] = self.radicand.to_dict()
        if self.lower_limit is not None:
            result["lower_limit"] = self.lower_limit.to_dict()
        if self.upper_limit is not None:
            result["upper_limit"] = self.upper_limit.to_dict()
        if self.expression is not None:
            result["expression"] = self.expression.to_dict()
        if self.rows is not None:
            result["rows"] = [[cell.to_dict() for cell in row] for row in self.rows]
        if self.left is not None:
            result["left"] = self.left.to_dict()
        if self.right is not None:
            result["right"] = self.right.to_dict()
        return result


class ExpressionParser:
    """
    Mathematical Structure Analysis Engine.
    
    Parses a flat list of detected symbols with bounding boxes into an AST
    by analyzing 2D spatial relationships.
    """
    
    def parse(self, symbols_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Main entrypoint to parse detected symbols into an AST.
        
        Args:
            symbols_data: List of dicts representing detected symbols:
                          [{"symbol": "x", "bbox": [x1, y1, x2, y2]}]
                          
        Returns:
            Dict[str, Any] or None: Serialized AST representation of the parsed expression.
        """
        if not symbols_data:
            return None
            
        # 1. Initialize symbols as ASTNode objects
        nodes = []
        for sym_info in symbols_data:
            nodes.append(self._make_initial_node(sym_info))
            
        # 2. Parse the list of nodes recursively
        ast = parse_expression_nodes(nodes)
        return ast.to_dict() if ast else None

    def _make_initial_node(self, sym_info: Dict[str, Any]) -> ASTNode:
        sym = sym_info["symbol"]
        bbox = sym_info["bbox"]
        
        # Determine classification
        if sym.isdigit() or (sym.replace('.', '', 1).isdigit() and sym.count('.') <= 1):
            return ASTNode(type='number', value=sym, bbox=bbox)
        elif sym in ('+', '-', '=', '*', '/', '^', '<', '>', 'leq', 'geq', 'neq'):
            return ASTNode(type='operator', value=sym, bbox=bbox)
        elif sym in ('(', ')', '[', ']', '{', '}'):
            return ASTNode(type='operator', value=sym, bbox=bbox)
        elif sym in ('int', 'sum', 'lim', 'sqrt'):
            return ASTNode(type='operator', value=sym, bbox=bbox)
        elif sym in ('sin', 'cos', 'tan', 'log'):
            return ASTNode(type='function', value=sym, bbox=bbox)
        elif sym in ('pi', 'inf'):
            return ASTNode(type='variable', value=sym, bbox=bbox)
        else:
            return ASTNode(type='variable', value=sym, bbox=bbox)


def parse_expression_nodes(nodes: List[ASTNode]) -> Optional[ASTNode]:
    """
    Recursively processes layout steps:
    1. Parentheses and Matrices
    2. Square Roots (nested roots)
    3. Fractions
    4. Limits / Integrals / Summations
    5. Baseline / Superscripts / Subscripts
    6. Binary Operator Precedence & Implicit Multiplication
    """
    if not nodes:
        return None
    if len(nodes) == 1:
        return nodes[0]
        
    # Sort nodes by x_min initially
    nodes = sorted(nodes, key=lambda n: n.bbox[0] if n.bbox else 0)
    
    # Step 1: Square roots (nested roots)
    nodes = parse_square_roots(nodes)
    
    # Step 2: Fractions
    nodes = parse_fractions(nodes)
    
    # Step 3: Parentheses and Matrices
    nodes = parse_parentheses_and_matrices(nodes)
    
    # Step 4: Integrals, Summations, and Limits
    nodes = parse_operators_with_limits(nodes)
    
    # Step 5: Baseline, Superscripts, and Subscripts
    nodes = parse_baseline_and_scripts(nodes)
    
    # Step 6: Binary Operators Precedence
    return parse_binary_operators(nodes)


def parse_parentheses_and_matrices(nodes: List[ASTNode]) -> List[ASTNode]:
    """
    Finds brackets and handles parenthesis groups or grid matrix structures.
    """
    while True:
        found = False
        best_open_idx = -1
        best_close_idx = -1
        
        # Scan for the inner-most matched pair of brackets
        for i, node in enumerate(nodes):
            if node.type == 'operator' and node.value in ('(', '[', '{'):
                best_open_idx = i
            elif node.type == 'operator' and node.value in (')', ']', '}') and best_open_idx != -1:
                best_close_idx = i
                found = True
                break
                
        if not found:
            break
            
        open_node = nodes[best_open_idx]
        close_node = nodes[best_close_idx]
        inner_nodes = nodes[best_open_idx+1 : best_close_idx]
        
        # Determine if it represents a matrix (grid arrangement)
        is_matrix = False
        rows_data = []
        if len(inner_nodes) > 0:
            avg_h = sum((n.bbox[3] - n.bbox[1]) for n in inner_nodes) / len(inner_nodes)
            # Sort inner nodes vertically by y_center
            sorted_inner = sorted(inner_nodes, key=lambda n: (n.bbox[1] + n.bbox[3]) / 2)
            
            current_row = [sorted_inner[0]]
            for node in sorted_inner[1:]:
                y_center_node = (node.bbox[1] + node.bbox[3]) / 2
                y_center_row = sum((n.bbox[1] + n.bbox[3]) / 2 for n in current_row) / len(current_row)
                if abs(y_center_node - y_center_row) > 0.55 * avg_h:
                    rows_data.append(current_row)
                    current_row = [node]
                else:
                    current_row.append(node)
            rows_data.append(current_row)
            
            open_h = open_node.bbox[3] - open_node.bbox[1]
            if len(rows_data) >= 2 and open_h > 1.6 * avg_h:
                is_matrix = True
                
        if is_matrix:
            # Cluster columns globally
            all_x_centers = sorted([(n.bbox[0] + n.bbox[2]) / 2 for n in inner_nodes])
            col_centers = []
            current_col = [all_x_centers[0]]
            avg_w = sum((n.bbox[2] - n.bbox[0]) for n in inner_nodes) / len(inner_nodes)
            for x in all_x_centers[1:]:
                avg_x_col = sum(current_col) / len(current_col)
                if x - avg_x_col > 0.6 * avg_w:
                    col_centers.append(avg_x_col)
                    current_col = [x]
                else:
                    current_col.append(x)
            col_centers.append(sum(current_col) / len(current_col))
            col_centers.sort()
            
            matrix_rows = []
            for row_nodes in rows_data:
                col_cells = [[] for _ in col_centers]
                for node in row_nodes:
                    node_x = (node.bbox[0] + node.bbox[2]) / 2
                    best_col_idx = min(range(len(col_centers)), key=lambda idx: abs(node_x - col_centers[idx]))
                    col_cells[best_col_idx].append(node)
                    
                parsed_row = []
                for cell_nodes in col_cells:
                    if cell_nodes:
                        cell_nodes_sorted = sorted(cell_nodes, key=lambda n: n.bbox[0])
                        cell_ast = parse_expression_nodes(cell_nodes_sorted)
                        parsed_row.append(cell_ast or ASTNode(type='empty', bbox=open_node.bbox))
                    else:
                        parsed_row.append(ASTNode(type='empty', bbox=open_node.bbox))
                matrix_rows.append(parsed_row)
                
            union_bbox = [
                min(open_node.bbox[0], close_node.bbox[0]),
                min(open_node.bbox[1], close_node.bbox[1]),
                max(open_node.bbox[2], close_node.bbox[2]),
                max(open_node.bbox[3], close_node.bbox[3])
            ]
            matrix_node = ASTNode(type='matrix', value=open_node.value, rows=matrix_rows, bbox=union_bbox)
            nodes = nodes[:best_open_idx] + [matrix_node] + nodes[best_close_idx+1:]
        else:
            union_bbox = [
                min(open_node.bbox[0], close_node.bbox[0]),
                min(open_node.bbox[1], close_node.bbox[1]),
                max(open_node.bbox[2], close_node.bbox[2]),
                max(open_node.bbox[3], close_node.bbox[3])
            ]
            inner_ast = parse_expression_nodes(inner_nodes)
            group_node = ASTNode(type='group', value=open_node.value, expression=inner_ast, bbox=union_bbox)
            nodes = nodes[:best_open_idx] + [group_node] + nodes[best_close_idx+1:]
            
    return nodes


def parse_square_roots(nodes: List[ASTNode]) -> List[ASTNode]:
    """
    Finds radicands inside square root radical symbols.
    Processes inner/smaller roots first to correctly handle nested roots.
    """
    while True:
        sqrt_indices = [i for i, n in enumerate(nodes) if n.type == 'operator' and n.value == 'sqrt']
        if not sqrt_indices:
            break
            
        # Sort by bounding box area ascending
        def get_area(idx):
            n = nodes[idx]
            return (n.bbox[2] - n.bbox[0]) * (n.bbox[3] - n.bbox[1])
            
        sqrt_indices.sort(key=get_area)
        best_sqrt_idx = sqrt_indices[0]
        sqrt_node = nodes[best_sqrt_idx]
        
        x1, y1, x2, y2 = sqrt_node.bbox
        w = x2 - x1
        h = y2 - y1
        
        # Calculate average width of non-sqrt nodes for scale comparison
        non_sqrt_nodes = [n for n in nodes if n.type != 'operator' or n.value != 'sqrt']
        avg_symbol_width = sum(n.bbox[2] - n.bbox[0] for n in non_sqrt_nodes) / (len(non_sqrt_nodes) or 1)
        
        is_tick_only = w < 1.4 * avg_symbol_width
        inside_indices = []
        
        if not is_tick_only:
            # Bounding box covers the expression underneath it
            for i, node in enumerate(nodes):
                if i == best_sqrt_idx:
                    continue
                nx_center = (node.bbox[0] + node.bbox[2]) / 2
                ny_center = (node.bbox[1] + node.bbox[3]) / 2
                if (x1 + 0.05 * w) < nx_center < (x2 + 5) and (y1 - 5) < ny_center < (y2 + 5):
                    inside_indices.append(i)
        else:
            # Tick only: grab consecutive horizontal symbols to the right at a similar vertical level
            right_nodes = []
            for i, node in enumerate(nodes):
                if i == best_sqrt_idx:
                    continue
                nx_center = (node.bbox[0] + node.bbox[2]) / 2
                ny_center = (node.bbox[1] + node.bbox[3]) / 2
                if nx_center > x1 + 0.1 * w:
                    right_nodes.append((i, nx_center, ny_center))
                    
            right_nodes.sort(key=lambda item: item[1])
            for idx, rx, ry in right_nodes:
                if (y1 - 0.25 * h) < ry < (y2 + 0.25 * h):
                    inside_indices.append(idx)
                else:
                    break
                    
        inside_nodes = [nodes[i] for i in inside_indices]
        remaining_nodes = [nodes[i] for i in range(len(nodes)) if i != best_sqrt_idx and i not in inside_indices]
        
        radicand_ast = parse_expression_nodes(sorted(inside_nodes, key=lambda n: n.bbox[0]))
        
        union_bbox = list(sqrt_node.bbox)
        for n in inside_nodes:
            union_bbox[0] = min(union_bbox[0], n.bbox[0])
            union_bbox[1] = min(union_bbox[1], n.bbox[1])
            union_bbox[2] = max(union_bbox[2], n.bbox[2])
            union_bbox[3] = max(union_bbox[3], n.bbox[3])
            
        sqrt_ast = ASTNode(type='sqrt', radicand=radicand_ast, bbox=union_bbox)
        remaining_nodes.append(sqrt_ast)
        nodes = sorted(remaining_nodes, key=lambda n: n.bbox[0])
        
    return nodes


def parse_fractions(nodes: List[ASTNode]) -> List[ASTNode]:
    """
    Identifies fraction lines (minus symbols with nodes both above and below them).
    Processes wider fraction bars first to handle nested fractions.
    """
    while True:
        minus_indices = [i for i, n in enumerate(nodes) if n.type == 'operator' and n.value == '-']
        if not minus_indices:
            break
            
        candidate_bars = []
        for idx in minus_indices:
            n = nodes[idx]
            w = n.bbox[2] - n.bbox[0]
            candidate_bars.append((idx, w))
            
        candidate_bars.sort(key=lambda item: item[1], reverse=True)
        
        fraction_found = False
        for idx, w in candidate_bars:
            bar_node = nodes[idx]
            bx1, by1, bx2, by2 = bar_node.bbox
            
            above_indices = []
            below_indices = []
            
            for i, node in enumerate(nodes):
                if i == idx:
                    continue
                nx_center = (node.bbox[0] + node.bbox[2]) / 2
                ny_center = (node.bbox[1] + node.bbox[3]) / 2
                
                # Check horizontal alignment within fraction bar's span
                h_overlap = (bx1 - 10) < nx_center < (bx2 + 10)
                
                if h_overlap:
                    if ny_center < by1:
                        above_indices.append(i)
                    elif ny_center > by2:
                        below_indices.append(i)
                        
            if above_indices and below_indices:
                numerator_nodes = [nodes[i] for i in above_indices]
                denominator_nodes = [nodes[i] for i in below_indices]
                remaining = [nodes[i] for i in range(len(nodes)) if i != idx and i not in above_indices and i not in below_indices]
                
                num_ast = parse_expression_nodes(sorted(numerator_nodes, key=lambda n: n.bbox[0]))
                den_ast = parse_expression_nodes(sorted(denominator_nodes, key=lambda n: n.bbox[0]))
                
                union_bbox = list(bar_node.bbox)
                for n in numerator_nodes + denominator_nodes:
                    union_bbox[0] = min(union_bbox[0], n.bbox[0])
                    union_bbox[1] = min(union_bbox[1], n.bbox[1])
                    union_bbox[2] = max(union_bbox[2], n.bbox[2])
                    union_bbox[3] = max(union_bbox[3], n.bbox[3])
                    
                frac_node = ASTNode(type='fraction', numerator=num_ast, denominator=den_ast, bbox=union_bbox)
                remaining.append(frac_node)
                nodes = sorted(remaining, key=lambda n: n.bbox[0])
                fraction_found = True
                break
                
        if not fraction_found:
            break
            
    return nodes


def parse_operators_with_limits(nodes: List[ASTNode]) -> List[ASTNode]:
    """
    Identifies summation, limit, and integral limits and expression bodies.
    """
    while True:
        op_indices = [i for i, n in enumerate(nodes) if n.type == 'operator' and n.value in ('sum', 'int', 'lim')]
        if not op_indices:
            break
            
        op_indices.sort()
        op_idx = op_indices[0]
        op_node = nodes[op_idx]
        op_val = op_node.value
        
        ox1, oy1, ox2, oy2 = op_node.bbox
        ow = ox2 - ox1
        
        above_indices = []
        below_indices = []
        
        for i, node in enumerate(nodes):
            if i == op_idx:
                continue
            nx_center = (node.bbox[0] + node.bbox[2]) / 2
            ny_center = (node.bbox[1] + node.bbox[3]) / 2
            
            # Limits can be centered or shifted to the right of the operator
            h_match = (ox1 - 15) < nx_center < (ox2 + ow * 0.9 + 15)
            
            if h_match:
                if ny_center < oy1:
                    above_indices.append(i)
                elif ny_center > oy2:
                    below_indices.append(i)
                    
        body_indices = []
        for i, node in enumerate(nodes):
            if i == op_idx or i in above_indices or i in below_indices:
                continue
            if node.bbox[0] > ox1:
                body_indices.append(i)
                
        above_nodes = [nodes[i] for i in above_indices]
        below_nodes = [nodes[i] for i in below_indices]
        body_nodes = [nodes[i] for i in body_indices]
        
        remaining = [nodes[i] for i in range(len(nodes)) if i != op_idx and i not in above_indices and i not in below_indices and i not in body_indices]
        
        lower_limit_ast = parse_expression_nodes(sorted(below_nodes, key=lambda n: n.bbox[0])) if below_nodes else None
        upper_limit_ast = parse_expression_nodes(sorted(above_nodes, key=lambda n: n.bbox[0])) if above_nodes else None
        body_ast = parse_expression_nodes(sorted(body_nodes, key=lambda n: n.bbox[0])) if body_nodes else None
        
        union_bbox = list(op_node.bbox)
        for n in above_nodes + below_nodes + body_nodes:
            union_bbox[0] = min(union_bbox[0], n.bbox[0])
            union_bbox[1] = min(union_bbox[1], n.bbox[1])
            union_bbox[2] = max(union_bbox[2], n.bbox[2])
            union_bbox[3] = max(union_bbox[3], n.bbox[3])
            
        node_type = 'integral' if op_val == 'int' else ('summation' if op_val == 'sum' else 'limit')
        new_node = ASTNode(
            type=node_type,
            lower_limit=lower_limit_ast,
            upper_limit=upper_limit_ast,
            expression=body_ast,
            bbox=union_bbox
        )
        remaining.append(new_node)
        nodes = sorted(remaining, key=lambda n: n.bbox[0])
        
    return nodes


def parse_baseline_and_scripts(nodes: List[ASTNode]) -> List[ASTNode]:
    """
    Extracts the horizontal baseline structure and resolves subscripts and superscripts.
    """
    if not nodes:
        return []
        
    # Sort left-to-right by x_center
    sorted_nodes = sorted(nodes, key=lambda n: (n.bbox[0] + n.bbox[2]) / 2)
    n_nodes = len(sorted_nodes)
    assigned = [False] * n_nodes
    baseline_elements = []
    
    for i in range(n_nodes):
        if assigned[i]:
            continue
            
        base_node = sorted_nodes[i]
        assigned[i] = True
        
        bx_center = (base_node.bbox[0] + base_node.bbox[2]) / 2
        by_center = (base_node.bbox[1] + base_node.bbox[3]) / 2
        bh = base_node.bbox[3] - base_node.bbox[1]
        
        superscript_nodes = []
        subscript_nodes = []
        
        for j in range(i + 1, n_nodes):
            if assigned[j]:
                continue
                
            candidate = sorted_nodes[j]
            cx_center = (candidate.bbox[0] + candidate.bbox[2]) / 2
            cy_center = (candidate.bbox[1] + candidate.bbox[3]) / 2
            ch = candidate.bbox[3] - candidate.bbox[1]
            
            # Check if vertically aligned as a baseline symbol
            is_aligned = abs(cy_center - by_center) < 0.25 * max(bh, ch)
            if is_aligned:
                break
                
            # Check vertical shift for subscript/superscript
            if cy_center < by_center - 0.22 * bh:
                superscript_nodes.append(candidate)
                assigned[j] = True
            elif cy_center > by_center + 0.22 * bh:
                subscript_nodes.append(candidate)
                assigned[j] = True
                
        baseline_elements.append((base_node, superscript_nodes, subscript_nodes))
        
    result_nodes = []
    for base_node, super_nodes, sub_nodes in baseline_elements:
        current_node = base_node
        
        if super_nodes:
            super_nodes_sorted = sorted(super_nodes, key=lambda n: n.bbox[0])
            exponent_ast_list = parse_baseline_and_scripts(super_nodes_sorted)
            if exponent_ast_list:
                exponent_node = parse_binary_operators(exponent_ast_list)
                union_bbox = list(current_node.bbox)
                for sn in super_nodes:
                    union_bbox[0] = min(union_bbox[0], sn.bbox[0])
                    union_bbox[1] = min(union_bbox[1], sn.bbox[1])
                    union_bbox[2] = max(union_bbox[2], sn.bbox[2])
                    union_bbox[3] = max(union_bbox[3], sn.bbox[3])
                current_node = ASTNode(type='superscript', base=current_node, exponent=exponent_node, bbox=union_bbox)
                
        if sub_nodes:
            sub_nodes_sorted = sorted(sub_nodes, key=lambda n: n.bbox[0])
            sub_ast_list = parse_baseline_and_scripts(sub_nodes_sorted)
            if sub_ast_list:
                sub_node = parse_binary_operators(sub_ast_list)
                union_bbox = list(current_node.bbox)
                for sn in sub_nodes:
                    union_bbox[0] = min(union_bbox[0], sn.bbox[0])
                    union_bbox[1] = min(union_bbox[1], sn.bbox[1])
                    union_bbox[2] = max(union_bbox[2], sn.bbox[2])
                    union_bbox[3] = max(union_bbox[3], sn.bbox[3])
                current_node = ASTNode(type='subscript', base=current_node, sub=sub_node, bbox=union_bbox)
                
        result_nodes.append(current_node)
        
    return result_nodes


def parse_binary_operators(nodes: List[ASTNode]) -> Optional[ASTNode]:
    """
    Constructs a binary expression tree from flat baseline nodes
    based on mathematical operator precedence. Handles prefix functions too.
    """
    if not nodes:
        return None
    if len(nodes) == 1:
        return nodes[0]
        
    # Operator Precedence (from right-to-left for left-associativity)
    # Precedence level 1: Relational operators (=, <, >, leq, geq, neq)
    for i in range(len(nodes) - 1, -1, -1):
        n = nodes[i]
        if n.type == 'operator' and n.value in ('=', '<', '>', 'leq', 'geq', 'neq'):
            left = parse_binary_operators(nodes[:i])
            right = parse_binary_operators(nodes[i+1:])
            union_bbox = list(n.bbox)
            for child in [left, right]:
                if child and child.bbox:
                    union_bbox[0] = min(union_bbox[0], child.bbox[0])
                    union_bbox[1] = min(union_bbox[1], child.bbox[1])
                    union_bbox[2] = max(union_bbox[2], child.bbox[2])
                    union_bbox[3] = max(union_bbox[3], child.bbox[3])
            return ASTNode(type='operator', value=n.value, left=left, right=right, bbox=union_bbox)
            
    # Precedence level 2: Additive operators (+, -)
    for i in range(len(nodes) - 1, -1, -1):
        n = nodes[i]
        if n.type == 'operator' and n.value in ('+', '-'):
            left = parse_binary_operators(nodes[:i])
            right = parse_binary_operators(nodes[i+1:])
            union_bbox = list(n.bbox)
            for child in [left, right]:
                if child and child.bbox:
                    union_bbox[0] = min(union_bbox[0], child.bbox[0])
                    union_bbox[1] = min(union_bbox[1], child.bbox[1])
                    union_bbox[2] = max(union_bbox[2], child.bbox[2])
                    union_bbox[3] = max(union_bbox[3], child.bbox[3])
            return ASTNode(type='operator', value=n.value, left=left, right=right, bbox=union_bbox)
            
    # Precedence level 3: Multiplicative operators (*, /)
    for i in range(len(nodes) - 1, -1, -1):
        n = nodes[i]
        if n.type == 'operator' and n.value in ('*', '/'):
            left = parse_binary_operators(nodes[:i])
            right = parse_binary_operators(nodes[i+1:])
            union_bbox = list(n.bbox)
            for child in [left, right]:
                if child and child.bbox:
                    union_bbox[0] = min(union_bbox[0], child.bbox[0])
                    union_bbox[1] = min(union_bbox[1], child.bbox[1])
                    union_bbox[2] = max(union_bbox[2], child.bbox[2])
                    union_bbox[3] = max(union_bbox[3], child.bbox[3])
            return ASTNode(type='operator', value=n.value, left=left, right=right, bbox=union_bbox)
            
    # Precedence level 4: Prefix functions and Implicit Multiplication
    left = nodes[0]
    right = parse_binary_operators(nodes[1:])
    union_bbox = list(left.bbox)
    if right and right.bbox:
        union_bbox[0] = min(union_bbox[0], right.bbox[0])
        union_bbox[1] = min(union_bbox[1], right.bbox[1])
        union_bbox[2] = max(union_bbox[2], right.bbox[2])
        union_bbox[3] = max(union_bbox[3], right.bbox[3])
        
    if left.type == 'function':
        return ASTNode(type='function', value=left.value, expression=right, bbox=union_bbox)
        
    return ASTNode(type='operator', value='*', left=left, right=right, bbox=union_bbox)
