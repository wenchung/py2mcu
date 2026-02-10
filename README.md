# py2mcu - Python to MCU C Compiler

[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=github)](https://github.com/sponsors/wenchung)
[![Support](https://img.shields.io/badge/Support-Buy%20Me%20a%20Coffee-FFDD00?logo=buymeacoffee)](https://github.com/sponsors/wenchung)

Write Python, test on PC, deploy to microcontrollers with automatic memory management.

## 📜 License

py2mcu is **dual-licensed**:

- **AGPLv3** - Free for open source projects, personal use, and education
- **Commercial License** - Required for proprietary/closed-source products

See [LICENSE_DUAL.md](LICENSE_DUAL.md) for details.

**Need a commercial license?** Contact: cwthome@gmail.com

---

## 💖 Support This Project

If py2mcu helps your work, consider sponsoring its development:

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?style=for-the-badge&logo=github)](https://github.com/sponsors/wenchung)

Your support helps maintain and improve py2mcu. Thank you! 🙏

---

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
        adc_value = rand() & 256;
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
def sum: uint8_t, uint8_t -> uint16_t:
    return a + b
```

Generated C code:
```c
uint16_t sum(uint8_t a, uint8_t b) {
    return a + b;
}
```

## Examples

See [examples/](https://github.com/wenchung/py2mcu/tree/main/examples):

- [demo1_led_blink.py](https://github.com/wenchung/py2mcu/blob/main/examples/demo1_led_blink.py) - Basic LED blinking with target-specific code
- [demo2_adc_average.py](https://github.com/wenchung/py2mcu/blob/main/examples/demo2_adc_average.py) - ADC reading and averaging
- [demo3_inline_c.py](https://github.com/wenchung/py2mcu/blob/main/examples/demo3_inline_c.py) - Inline C code integration

## Contributing

We welcome contributions! Please open an issue or submit a pull request.

## Contact

For commercial licensing or support: cwthome@gmail.com
