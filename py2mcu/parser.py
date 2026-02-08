"""
Python AST parser
"""
import ast
from pathlib import Path

def parse_python_file(filepath: str) -> ast.Module:
    """Parse a Python file and return AST"""
    source = Path(filepath).read_text()
    return ast.parse(source, filename=filepath)

def parse_python_string(source: str) -> ast.Module:
    """Parse Python source string and return AST"""
    return ast.parse(source)
