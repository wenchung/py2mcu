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

## Target Platform Support

py2mcu uses a unified target macro system for cross-platform development:

### Compilation Targets

- `--target pc` → Generates `#define TARGET_PC 1` - Desktop simulation
- `--target stm32f4` → Generates `#define TARGET_STM32F4 1` - STM32F4 MCUs
- `--target esp32` → Generates `#define TARGET_ESP32 1` - ESP32 MCUs
- `--target arduino` → Generates `#define TARGET_ARDUINO 1` - Arduino boards

### Platform-Specific Code

Write code that adapts to the target platform using `#ifdef` directives:

```python
def read_sensor() -> int:
    """Read sensor value
    
    __C_CODE__
    #ifdef TARGET_PC
        return rand() % 1024;  // Simulate sensor on PC
    #elif defined(TARGET_STM32F4)
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY);
        return HAL_ADC_GetValue(&hadc1);
    #elif defined(TARGET_ESP32)
        return analogRead(34);
    #endif
    """
    import random
    return random.randint(0, 1023)
```

### Development Workflow

1. **Develop and test on PC:**
   ```bash
   py2mcu compile my_code.py --target pc -o build/
   gcc build/my_code.c -o build/my_code
   ./build/my_code
   ```

2. **Deploy to target MCU:**
   ```bash
   py2mcu compile my_code.py --target stm32f4 -o build/
   # Use your MCU toolchain to build and flash
   ```

This unified approach enables rapid development on PC with immediate feedback, then seamless deployment to embedded targets.

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
python -m py2mcu.cli compile examples/demo1_led_blink.py --target stm32f4 -o build/
```
