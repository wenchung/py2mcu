# py2mcu - Python to MCU C Compiler

Write Python, test on PC, deploy to microcontrollers with automatic memory management.

## Features

- **Python to C Translation**: Converts typed Python code to efficient C
- **Automatic Memory Management**: Arena allocator + reference counting
- **Inline C Support**: Write performance-critical code directly in C
- **Cross-Platform Development**: Test on PC, deploy to MCU with unified target macros
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

## Type System

py2mcu supports standard C integer types as Python type annotations. Simply use C type names directly:

### Basic Example

```python
def uart_example() -> None:
    # unsigned char for UART transmission
    tx_byte: uint8_t = 0x41  # 'A'
    
    # buffer array (defined in inline C)
    __C_CODE__ = """
    uint8_t buffer[256];
    buffer[0] = tx_byte;
    """
    
def adc_example() -> None:
    # 8-bit ADC value
    adc_value: uint8_t = 0
    
    __C_CODE__ = """
    #ifdef TARGET_PC
        adc_value = rand() % 256;
    #else
        adc_value = HAL_ADC_GetValue(&hadc1) & 0xFF;
    #endif
    """
```

### Type Reference Table

| Python Annotation | C Type | Range |
|------------------|--------|-------|
| `uint8_t` | `uint8_t` | 0 ~ 255 |
| `uint16_t` | `uint16_t` | 0 ~ 65535 |
| `uint32_t` | `uint32_t` | 0 ~ 4294967295 |
| `int8_t` | `int8_t` | -128 ~ 127 |
| `int16_t` | `int16_t` | -32768 ~ 32767 |
| `int32_t` or `int` | `int32_t` | -2147483648 ~ 2147483647 |
| `float` | `float` | 32-bit floating point |
| `bool` | `bool` | true/false |

### Key Points

- **Use C type names directly** as Python type annotations
- py2mcu preserves these type names in generated C code
- `#include <stdint.h>` is automatically added
- Default `int` maps to `int32_t` (signed 32-bit)
- For unsigned 32-bit, explicitly use `uint32_t`

### Example

```python
byte: uint8_t = 255        # ✅ unsigned char (0-255)
value: int = -100          # ✅ int32_t (signed)
counter: uint32_t = 1000   # ✅ unsigned 32-bit
temperature: float = 25.5  # ✅ 32-bit float
```

## print() to printf() Conversion

py2mcu automatically converts Python's `print()` statements to C's `printf()` with intelligent formatting.

### Conversion Rules

#### 1. Empty print()
```python
print()
```
↓ Converts to:
```c
printf("\n");
```

#### 2. Single argument
```python
print(42)
print(x)
```
↓ Converts to:
```c
printf("%d\n", 42);
printf("%d\n", x);
```

#### 3. String with multiple arguments
```python
print("Value:", x)
print("x =", x, "y =", y)
```
↓ Converts to:
```c
printf("Value: %d\n", x);
printf("x = %d y = %d\n", x, y);
```

### How It Works

The conversion logic (from `codegen.py` lines 317-332):

1. **String prefix + arguments**: Combines the first string with `%d` placeholders for remaining arguments
2. **Auto-append newline**: Adds `\n` to every printf call
3. **Format specifier**: Uses `%d` (integer) for all non-string arguments by default

### Current Limitations

⚠️ **Fixed format specifier**: All numeric arguments use `%d` (integer format)

For advanced formatting (floats, hex, etc.), use inline C:
```python
__C_CODE__ = """
printf("Float: %.2f, Hex: 0x%X\\n", voltage, register_val);
"""
```

### Best Practices

**✅ Recommended usage:**
```python
print("Debug: value =", x)      # Simple labeled output
print(counter)                   # Single variable
print("ADC:", adc_value)        # Sensor readings
```

**⚠️ Use inline C for:**
```python
# Complex formatting needs
__C_CODE__ = """
printf("Temperature: %.1f°C\\n", temp);
printf("Status: 0x%04X\\n", status_reg);
"""
```

## Target Platform Support

py2mcu uses a unified target macro system for cross-platform development:

### Target Macros

| Target | Macro | Description |
|-------|------|------------|
| PC (test) | `TARGETE_PC` | Testing on desktop |
| STM32 | `TARGET_STM32` | ARM Cortex-M MCUs |
| ESP32 | `TARGETE_ESP32` | Espressif ESP32 |
| RP2040 | `TARGET_RP2040` | Raspberry Pi Pico |

### Usage Example

```python
def read_sensor() -> int:
    __C_CODE__ = """
    #ifdef TARGET_PC
        return rand() % 100;  // Simulated data
    #else
        return HAL_ADC_GetValue(&hadc1);  // Real hardware
    #endif
    """
```

Compile with target selection:
```bash
py2mcu compile my_code.py --target pc      # ✅ TARGET_PC defined
py2mcu compile my_code.py --target stm32  # ✅ TARGET_STM32 defined
```

## Examples

See the [examples/](examples/) directory for more demos:

- `demo1_led_blink.py` - Basic LED blinking
- `demo2_adc_average.py` - ADC reading with averaging
- `demo3_inline_c.py` - Inline C code demonstration
- `demo4_timer_pwm.py` - Timer and PWM control

## Project Structure

```
py2mcu/
├── python-path-to-muc/    # Project root (also contains `py_path_to_muc` package)
├── py2mcu/                  # Python package
│   ├── __init__.py
│   ├── parser.py              # Python AST parser
│   ├── codegen.py             # C code generator
│   ├── cli.py                 # Command line interface
│   └── runtime/              # Runtime libraries
│       ├── gc_runtime.c
│       └── gc_runtime.h
├── examples/                # Example Python files
├── tests/                   # Test suite
├── setup.py                # Package installation
└── README.md               # Documentation
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License
