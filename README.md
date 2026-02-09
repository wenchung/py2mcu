# py2mcu - Python to MCU C Compiler

Write Python, test on PC, deploy to microcontrollers with automatic memory management.

## Features

- **Python to C Translation**: Converts typed Python code to efficient C
- **Automatic Memory Management**: Arena allocator + reference counting
- **Inline C Support**: Write performance-critical code directly in C
- **PC Testing**: Test your code on PC before deploying to MCU
- **Multiple MCU Support**: STM32, ESP32, RP2040, and more

## Quick Start

### Option 1: Direct Usage (No Installation Required)

```bash
# Clone the repository
git clone https://github.com/wenchung/py2mcu.git
cd py2mcu

# Run compiler directly
python -m py2mcu.cli compile examples/demo1_led_blink.py --target pc

# Or use the direct script
python py2mcu/cli.py compile examples/demo1_led_blink.py --target pc
```

### Option 2: Install as Package

```bash
pip install -e .
py2mcu compile examples/demo1_led_blink.py --target pc
```

### Hello World

```python
# hello.py
def main() -> None:
    print("Hello from py2mcu!")

if __name__ == "__main__":
    main()
```

Compile to C:
```bash
# Without installation
python -m py2mcu.cli compile hello.py --target pc

# With installation
py2mcu compile hello.py --target pc
```

## Architecture

```
Python Source → AST Parser → Type Checker → C Code Generator → MCU Compiler → Binary
```

## Memory Management

py2mcu uses a hybrid memory management strategy:

- **Stack allocation** for fixed-size local variables
- **Arena allocator** for temporary allocations (fast, automatic cleanup)
- **Reference counting** for heap objects that escape function scope

### Example

```python
def process_sensor():
    # Stack allocation (compile-time known size)
    readings: List[int, 10] = [0] * 10

    # Arena allocation (automatic cleanup)
    with arena():
        temp = process_data(readings)

    # Reference counting (escapes function)
    result = create_report(temp)
    return result  # caller owns the reference
```

## Inline C Support

```python
from py2mcu import inline_c

@inline_c("""
uint32_t fast_gpio_read(int pin) {
    return GPIOC->IDR & (1 << pin);
}
""")
def read_gpio(pin: int) -> int:
    return fast_gpio_read(pin)
```

## Examples

See the `examples/` directory for complete demos:

- `demo1_led_blink.py` - Basic control flow and GPIO
- `demo2_adc_average.py` - Array processing and calculations
- `demo3_inline_c.py` - Inline C for performance-critical code
- `demo4_memory.py` - Memory management showcase
- `demo5_docstring_c.py` - Using docstrings for inline C code
- `demo6_defines.py` - Module-level constants with #define

### Running Examples (Without Installation)

```bash
# Compile and test on PC (use --output or -o)
python -m py2mcu.cli compile examples/demo1_led_blink.py --target pc --output build/
gcc -Iruntime build/demo1_led_blink.c runtime/gc_runtime.c -o demo1
./demo1

# Generate C code for STM32F4 (shorthand -o also works)
python -m py2mcu.cli compile examples/demo2_adc_average.py --target stm32f4 -o build/

# Compile all demos
python -m py2mcu.cli compile examples/demo3_inline_c.py --target pc -o build/
python -m py2mcu.cli compile examples/demo4_memory.py --target pc -o build/
python -m py2mcu.cli compile examples/demo5_docstring_c.py --target pc -o build/
python -m py2mcu.cli compile examples/demo6_defines.py --target pc -o build/

# Compile generated C code (requires -Iruntime for header files)
gcc -Iruntime build/demo1_led_blink.c runtime/gc_runtime.c -o demo1
gcc -Iruntime build/demo3_inline_c.c runtime/gc_runtime.c -o demo3
gcc -Iruntime build/demo4_memory.c runtime/gc_runtime.c -o demo4

# Check generated code
cat build/demo2_adc_average.c
```

## Documentation

- [User Guide](docs/guide.md)
- [Language Reference](docs/language.md)
- [Memory Management](docs/memory.md)
- [Index](docs/INDEX.md)

## Requirements

- Python 3.10+
- GCC or any C compiler for platform-targets
- MCU development tools (STM32Cube, ESP-IDF, etc.)

## License

MIT License - see LICENSE file for details.
