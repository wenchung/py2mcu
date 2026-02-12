"""
C code generator from Python AST
"""
import ast
from typing import List, Dict, Any
from .parser import extract_variable_modifiers

class CCodeGenerator(ast.NodeVisitor):
    """
    Generate C code from Python AST
    """

    def __init__(self, target: str = 'pc'):
        self.target = target
        self.code: List[str] = []
        self.indent_level = 0
        # PC target needs time.h for nanosleep
        if target == 'pc':
            self.includes = set(['<stdint.h>', '<stdbool.h>', '<stdio.h>', '<time.h>'])
        else:
            self.includes = set(['<stdint.h>', '<stdbool.h>', '<stdio.h>'])
        self.in_function = False  # Track if we're inside a function
        self.local_vars = set()  # Track declared local variables

    def generate(self, tree: ast.Module) -> str:
        """Generate C code from AST"""
        # Store source code for modifier extraction
        if hasattr(tree, '_source'):
            self._source_code = tree._source
        
        self.code = []

        # Add includes
        self._add_includes()

        # Add #define constants (from @#define annotations)
        if hasattr(tree, 'py2mcu_defines') and tree.py2mcu_defines:
            self._add_defines(tree.py2mcu_defines)
            self.emit("")

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
        
        # Add target-specific macro definitions
        if self.target == 'stm32f4':
            self.emit("#define STM32F4 1")
            self.emit("")
        elif self.target == 'pc':
            self.emit("#define TARGET_PC 1")
            self.emit("")

    def _add_defines(self, defines: List[Dict]):
        """Generate #define directives from @#define annotations
        
        Args:
            defines: List of dicts with 'name', 'value', 'type' (optional)
        """
        if not defines:
            return
        
        self.emit("// Constants from @#define annotations")
        
        for d in defines:
            name = d['name']
            value = d['value']
            c_type = d.get('type')
            
            # Convert Python values to C format
            c_value = self._python_value_to_c(value)
            
            if c_type:
                # Typed constant: #define LED_PIN ((uint8_t)13)
                self.emit(f"#define {name} (({c_type}){c_value})")
            else:
                # Simple define: #define MAX_SIZE 10
                self.emit(f"#define {name} {c_value}")
    
    def _python_value_to_c(self, value_str: str) -> str:
        """Convert Python literal to C format
        
        Examples:
            True -> 1
            False -> 0
            "text" -> "text"
            1000 * 60 -> (1000 * 60)
        """
        value_str = value_str.strip()
        
        # Boolean conversion
        if value_str == 'True':
            return '1'
        elif value_str == 'False':
            return '0'
        
        # String literals - keep as is
        if value_str.startswith('"') or value_str.startswith("'"):
            return value_str.replace("'", '"')
        
        # Expression with operators - wrap in parentheses
        if any(op in value_str for op in ['*', '+', '-', '/', '<<', '>>', '&', '|', '^']):
            return f"({value_str})"
        
        # Simple numeric or identifier - use as is
        return value_str

    def visit_Module(self, node: ast.Module):
        """Visit module node"""
        for item in node.body:
            self.visit(item)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Generate C function from Python function"""

        # Special handling for main() function
        if node.name == "main":
            if self.target == "pc":
                # PC target: int main(void) with return 0
                self.emit("int main(void) {")
            else:
                # Embedded target: void main(void)
                self.emit("void main(void) {")
            self.indent_level += 1
            self.in_function = True
            self.local_vars.clear()
            
            # Generate function body
            for stmt in node.body:
                self.visit(stmt)
            
            # Add return 0 for PC target
            if self.target == "pc":
                self.emit("return 0;")
            
            self.in_function = False
            self.local_vars.clear()
            self.indent_level -= 1
            self.emit("}")
            self.emit("")
            return

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
        self.in_function = True
        self.local_vars.clear()  # Reset local variables for this function

        # Check if function has docstring with C code
        c_code = self._extract_c_code_from_docstring(node)
        
        if c_code:
            # Use the C code from docstring - preserve all lines including preprocessor directives
            for line in c_code.split('\n'):
                # Preserve preprocessor directives without modification
                stripped = line.strip()
                if stripped.startswith('#'):
                    # Output preprocessor directive at column 0 (no indent)
                    self.code.append(stripped)
                elif stripped:
                    # Regular C code with proper indentation
                    self.emit(stripped)
        else:
            # Generate from Python body
            for stmt in node.body:
                self.visit(stmt)

        self.in_function = False
        self.local_vars.clear()
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
        # Skip standalone string literals (docstrings)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return
        
        expr = self._expr_to_c(node.value)
        self.emit(f"{expr};")

    def visit_If(self, node: ast.If):
        """Generate if statement"""
        # Skip if __name__ == '__main__' blocks entirely
        if self._is_main_guard(node.test):
            # Don't generate anything - we have main() function already
            return
        
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

    
    def _get_storage_class_specifiers(self, modifiers: dict, base_type: str) -> str:
        """Generate C storage class specifiers from modifiers.

        Args:
            modifiers: Dict with 'const', 'public', 'volatile' flags
            base_type: The base C type (e.g., 'int', 'uint8_t')

        Returns:
            Complete type declaration with modifiers in correct C order

        Examples:
            {'const': True, 'public': False, 'volatile': False}, 'int' -> 'static const int'
            {'const': True, 'public': True, 'volatile': False}, 'int' -> 'const int'
            {'const': False, 'public': False, 'volatile': True}, 'int' -> 'static volatile int'
        """
        parts = []

        # Static (default unless public)
        if not modifiers.get('public', False):
            parts.append('static')

        # Volatile
        if modifiers.get('volatile', False):
            parts.append('volatile')

        # Const
        if modifiers.get('const', False):
            parts.append('const')

        # Base type
        parts.append(base_type)

        return ' '.join(parts)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Generate annotated assignment"""
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            var_type = self._map_type(node.annotation)

            if node.value:
                value = self._expr_to_c(node.value)
                if self.in_function:
                    # Inside function: regular declaration
                    self.emit(f"{var_type} {var_name} = {value};")
                    self.local_vars.add(var_name)
                else:
                    # Global variable: check for modifiers
                    # Extract modifiers from comment above declaration
                    modifiers = {'const': False, 'public': False, 'volatile': False}

                    # Get source code if available (for modifier extraction)
                    if hasattr(self, '_source_code'):
                        modifiers = extract_variable_modifiers(self._source_code, node.lineno)

                    # Generate type with storage class specifiers
                    full_type = self._get_storage_class_specifiers(modifiers, var_type)

                    self.emit(f"{full_type} {var_name} = {value};")
            else:
                # Declaration without value
                if self.in_function:
                    self.emit(f"{var_type} {var_name};")
                    self.local_vars.add(var_name)
                else:
                    # Global declaration
                    modifiers = {'const': False, 'public': False, 'volatile': False}
                    if hasattr(self, '_source_code'):
                        modifiers = extract_variable_modifiers(self._source_code, node.lineno)

                    full_type = self._get_storage_class_specifiers(modifiers, var_type)
                    self.emit(f"{full_type} {var_name};")

    
    def visit_Assign(self, node: ast.Assign):
        """Generate assignment"""
        value = self._expr_to_c(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if self.in_function:
                    # Inside function: check if variable needs declaration
                    if var_name not in self.local_vars:
                        # Check if this is a self-referencing assignment (e.g., count = count + 1)
                        uses_itself = self._expr_uses_name(node.value, var_name)
                        if uses_itself:
                            # Self-reference means it's already declared somewhere - just assign
                            self.emit(f"{var_name} = {value};")
                            self.local_vars.add(var_name)
                        else:
                            # First assignment: declare with inferred type
                            var_type = self._infer_type_from_value(node.value)
                            self.emit(f"{var_type} {var_name} = {value};")
                            self.local_vars.add(var_name)
                    else:
                        # Subsequent assignment
                        self.emit(f"{var_name} = {value};")
                else:
                    # Module-level: declare as const global
                    var_type = self._infer_type_from_value(node.value)
                    self.emit(f"const {var_type} {var_name} = {value};")

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
            
            # Convert print() to printf()
            if func_name == "print":
                func_name = "printf"
                # For printf, we need a format string
                if node.args:
                    # Simple conversion: just add \n at the end
                    args = ", ".join(self._expr_to_c(arg) for arg in node.args)
                    # If first arg is a string, add %s for remaining args
                    if len(node.args) > 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        format_str = node.args[0].value + " " + " ".join(["%d"] * (len(node.args) - 1)) + "\\n"
                        remaining_args = ", ".join(self._expr_to_c(arg) for arg in node.args[1:])
                        return f'{func_name}("{format_str}", {remaining_args})'
                    else:
                        # Single argument or all need formatting
                        return f'{func_name}("%d\\n", {args})'
                else:
                    return f'{func_name}("\\n")'
            
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

    def _infer_type_from_value(self, node: ast.AST) -> str:
        """Infer C type from Python value node"""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "bool"
            elif isinstance(node.value, int):
                return "int32_t"
            elif isinstance(node.value, float):
                return "float"
            elif isinstance(node.value, str):
                return "char*"
        return "int32_t"  # Default fallback

    def _expr_uses_name(self, expr: ast.AST, name: str) -> bool:
        """Check if expression uses a specific variable name"""
        class NameChecker(ast.NodeVisitor):
            def __init__(self):
                self.uses_name = False
            
            def visit_Name(self, node):
                if node.id == name:
                    self.uses_name = True
        
        checker = NameChecker()
        checker.visit(expr)
        return checker.uses_name
    
    def _expr_uses_name(self, expr: ast.AST, name: str) -> bool:
        """Check if expression uses a specific variable name"""
        class NameChecker(ast.NodeVisitor):
            def __init__(self):
                self.uses_name = False
            
            def visit_Name(self, node):
                if node.id == name:
                    self.uses_name = True
        
        checker = NameChecker()
        checker.visit(expr)
        return checker.uses_name
    
    def _is_main_guard(self, node: ast.AST) -> bool:
        """Check if this is the if __name__ == '__main__' pattern"""
        if isinstance(node, ast.Compare):
            # Check for __name__ == '__main__' or '__main__' == __name__
            if (isinstance(node.left, ast.Name) and node.left.id == '__name__' and
                len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq) and
                len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant) and
                node.comparators[0].value == '__main__'):
                return True
            
            if (isinstance(node.left, ast.Constant) and node.left.value == '__main__' and
                len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq) and
                len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Name) and
                node.comparators[0].id == '__name__'):
                return True
        
        return False

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
                    if found_marker:
                        # Preserve ALL lines after marker (including empty lines and preprocessor directives)
                        c_lines.append(line)
                
                return '\n'.join(c_lines)
        
        return ""

    def emit(self, line: str):
        """Emit a line of C code with proper indentation"""
        indent = "    " * self.indent_level
        self.code.append(indent + line)