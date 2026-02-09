"""
C code generator from Python AST
"""
import ast
from typing import List, Dict, Any

class CCodeGenerator(ast.NodeVisitor):
    """
    Generate C code from Python AST
    """

    def __init__(self, target: str = 'pc'):
        self.target = target
        self.code: List[str] = []
        self.indent_level = 0
        self.includes = set(['<stdint.h>', '<stdbool.h>', '<stdio.h>'])

    def generate(self, tree: ast.Module) -> str:
        """Generate C code from AST"""
        self.code = []

        # Add includes
        self._add_includes()

        # Add GC runtime
        self.emit('#include "gc_runtime.h"')
        self.emit("")

        # Visit all nodes
        self.visit(tree)

        return '\n'.join(self.code)

    def _add_includes(self):
        """Add C includes"""
        for include in sorted(self.includes):
            self.emit(f"#include {include}")
        self.emit("")

    def visit_Module(self, node: ast.Module):
        """Visit module node"""
        for item in node.body:
            self.visit(item)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Generate C function from Python function"""

        # Get return type
        return_type = self._map_type(node.returns) if node.returns else "void"

        # Generate parameter list
        params = []
        for arg in node.args.args:
            arg_type = self._map_type(arg.annotation) if arg.annotation else "int32_t"
            params.append(f"{arg_type} {arg.arg}")

        params_str = ", ".join(params) if params else "void"

        # Function signature
        self.emit(f"{return_type} {node.name}({params_str}) {{")
        self.indent_level += 1

        # Check if function has docstring with C code
        c_code = self._extract_c_code_from_docstring(node)
        
        if c_code:
            # Use the C code from docstring
            for line in c_code.split('\n'):
                if line.strip():
                    self.emit(line.strip())
        else:
            # Generate from Python body
            for stmt in node.body:
                self.visit(stmt)

        self.indent_level -= 1
        self.emit("}")
        self.emit("")

    def visit_Return(self, node: ast.Return):
        """Generate return statement"""
        if node.value:
            expr = self._expr_to_c(node.value)
            self.emit(f"return {expr};")
        else:
            self.emit("return;")

    def visit_Expr(self, node: ast.Expr):
        """Generate expression statement"""
        expr = self._expr_to_c(node.value)
        self.emit(f"{expr};")

    def visit_If(self, node: ast.If):
        """Generate if statement"""
        condition = self._expr_to_c(node.test)
        self.emit(f"if ({condition}) {{")
        self.indent_level += 1

        for stmt in node.body:
            self.visit(stmt)

        self.indent_level -= 1

        if node.orelse:
            self.emit("} else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1

        self.emit("}")

    def visit_While(self, node: ast.While):
        """Generate while loop"""
        condition = self._expr_to_c(node.test)
        self.emit(f"while ({condition}) {{")
        self.indent_level += 1

        for stmt in node.body:
            self.visit(stmt)

        self.indent_level -= 1
        self.emit("}")

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Generate annotated assignment"""
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            var_type = self._map_type(node.annotation)

            if node.value:
                value = self._expr_to_c(node.value)
                self.emit(f"{var_type} {var_name} = {value};")
            else:
                self.emit(f"{var_type} {var_name};")

    def visit_Assign(self, node: ast.Assign):
        """Generate assignment"""
        value = self._expr_to_c(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.emit(f"{target.id} = {value};")

    def _expr_to_c(self, node: ast.AST) -> str:
        """Convert Python expression to C expression"""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "true" if node.value else "false"
            elif isinstance(node.value, str):
                return f'"{node.value}"'
            else:
                return str(node.value)

        elif isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.BinOp):
            left = self._expr_to_c(node.left)
            right = self._expr_to_c(node.right)
            op = self._op_to_c(node.op)
            return f"({left} {op} {right})"

        elif isinstance(node, ast.Compare):
            left = self._expr_to_c(node.left)
            op = self._compare_op_to_c(node.ops[0])
            right = self._expr_to_c(node.comparators[0])
            return f"({left} {op} {right})"

        elif isinstance(node, ast.Call):
            func_name = self._expr_to_c(node.func)
            args = ", ".join(self._expr_to_c(arg) for arg in node.args)
            return f"{func_name}({args})"

        else:
            return "/* unknown expression */"

    def _op_to_c(self, op: ast.operator) -> str:
        """Map Python operator to C operator"""
        op_map = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.FloorDiv: '/',
        }
        return op_map.get(type(op), '?')

    def _compare_op_to_c(self, op: ast.cmpop) -> str:
        """Map Python comparison operator to C"""
        op_map = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
        }
        return op_map.get(type(op), '?')

    def _map_type(self, node: ast.AST) -> str:
        """Map Python type to C type"""
        if node is None:
            return "void"

        if isinstance(node, ast.Name):
            type_map = {
                'int': 'int32_t',
                'float': 'float',
                'bool': 'bool',
                'str': 'const char*',
                'None': 'void',
            }
            return type_map.get(node.id, node.id)

        elif isinstance(node, ast.Constant):
            if node.value is None:
                return "void"

        return "void"

    def _extract_c_code_from_docstring(self, node: ast.FunctionDef) -> str:
        """Extract C code from function docstring if marked with __C_CODE__"""
        if not node.body:
            return ""
        
        # Check if first statement is a docstring
        first_stmt = node.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
            docstring = first_stmt.value.value
            if isinstance(docstring, str) and "__C_CODE__" in docstring:
                # Extract C code after the marker
                lines = docstring.split('\n')
                c_lines = []
                found_marker = False
                
                for line in lines:
                    if "__C_CODE__" in line:
                        found_marker = True
                        continue
                    if found_marker and line.strip():
                        c_lines.append(line)
                
                return '\n'.join(c_lines)
        
        return ""

    def emit(self, line: str):
        """Emit a line of C code with proper indentation"""
        indent = "    " * self.indent_level
        self.code.append(indent + line)