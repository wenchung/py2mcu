"""
Python AST parser
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional

def parse_python_file(filepath: str) -> ast.Module:
    """Parse a Python file and return AST"""
    source = Path(filepath).read_text()
    tree = ast.parse(source, filename=filepath)
    
    # Extract @#define annotations and attach to tree
    defines = extract_define_constants(source)
    tree.py2mcu_defines = defines
    
    return tree

def parse_python_string(source: str) -> ast.Module:
    """Parse Python source string and return AST"""
    tree = ast.parse(source)
    
    # Extract @#define annotations and attach to tree
    defines = extract_define_constants(source)
    tree.py2mcu_defines = defines
    
    return tree

def extract_define_constants(source: str) -> List[Dict]:
    """Extract constants marked with @#define comment
    
    Supports formats:
        MAX_SIZE = 10  # @#define
        LED_PIN = 13  # @#define uint8_t
        TIMEOUT = 1000 * 60  # @#define
        DEBUG = True  # @#define
        NAME = "STM32"  # @#define
    
    Returns:
        List of dicts with 'name', 'value', 'type' (optional)
    """
    # Pattern: variable_name = value  # @#define [optional_type]
    pattern = r'^\s*([A-Z_][A-Z0-9_]*)\s*[=:]\s*(.+?)\s*#\s*@#define(?:\s+(\w+))?'
    
    defines = []
    for line in source.split('\n'):
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            name = match.group(1)
            value_str = match.group(2).strip()
            c_type = match.group(3)  # optional type hint
            
            # Clean up value (remove trailing comments)
            value_str = value_str.split('#')[0].strip()
            
            defines.append({
                'name': name,
                'value': value_str,
                'type': c_type,
                'line': line.strip()
            })
    
    return defines
