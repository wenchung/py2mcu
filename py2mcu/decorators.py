"""
Decorators for py2mcu compiler hints
"""

def inline_c(c_code: str):
    """
    Decorator to embed inline C code

    Usage:
        @inline_c('''
        int fast_add(int a, int b) {
            return a + b;
        }
        ''')
        def add(a: int, b: int) -> int:
            return fast_add(a, b)
    """
    def decorator(func):
        func._inline_c = c_code
        return func
    return decorator

def arena(func=None):
    """
    Context manager for arena memory allocation

    Usage:
        with arena():
            temp = large_computation()
        # temp is automatically freed
    """
    if func is None:
        # Used as context manager
        class ArenaContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return ArenaContext()
    else:
        # Used as decorator
        func._use_arena = True
        return func

def static_alloc(func):
    """
    Decorator to force static/stack allocation
    """
    func._static_alloc = True
    return func
