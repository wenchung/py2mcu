# py2mcu Examples

This directory contains example programs demonstrating py2mcu features.

## Examples Overview

## Target Platform Support

py2mcu uses a unified target macro system: `--target XX` generates `#define TARGET_XX 1`

### Available Targets

- `--target pc` → `#define TARGET_PC 1` - Desktop simulation
- `--target stm32f4` → `#define TARGET_STM32F4 1` - STM32F4 microcontrollers
- `--target esp32` → `#define TARGET_ESP32 1` - ESP32 microcontrollers
- `--target arduino` → `#define TARGET_ARDUINO 1` - Arduino boards

### Platform-Specific Code

Use `#ifdef TARGET_XX` in your `__C_CODE__` sections or inline C code:

```python
__C_CODE__ = """
#ifdef TARGET_PC
    printf("Running on PC\\n");
#elif defined(TARGET_STM32F4)
    HAL_UART_Transmit(&huart2, (uint8_t*)"Running on STM32\\n", 18, HAL_MAX_DELAY);
#endif
"""
```

### Testing Workflow

1. **Develop & Test on PC:**
   ```bash
   py2mcu compile examples/demo1_led_blink.py --target pc -o build/
   gcc build/demo1_led_blink.c -o build/demo1_led_blink
   ./build/demo1_led_blink
   ```

2. **Deploy to MCU:**
   ```bash
   py2mcu compile examples/demo1_led_blink.py --target stm32f4 -o build/
   # Use your MCU toolchain to build and flash
   ```

## Demo Programs

### demo1_led_blink.py - Basic Control Flow
Demonstrates fundamental concepts:
- Function definitions with type annotations
- While loops and conditionals
- Basic GPIO operations
- Platform-independent delay

**Compile for PC:**
```bash
py2mcu compile examples/demo1_led_blink.py --target pc -o build/
gcc build/demo1_led_blink.c -o build/demo1_led_blink
./build/demo1_led_blink
```

**Compile for STM32F4:**
```bash
py2mcu compile examples/demo1_led_blink.py --target stm32f4 -o build/
```

### demo2_adc_average.py - Array Processing
Demonstrates data processing with **TARGET_PC support**:
- Fixed-size arrays
- For/while loops with arrays
- Integer arithmetic and division
- Sensor data processing patterns
- PC simulation for ADC and GPIO

**Compile for PC:**
```bash
py2mcu compile examples/demo2_adc_average.py --target pc -o build/
gcc build/demo2_adc_average.c -o build/demo2_adc_average
./build/demo2_adc_average
```

**Compile for STM32F4:**
```bash
py2mcu compile examples/demo2_adc_average.py --target stm32f4 -o build/
```

### demo3_inline_c.py - Performance Optimization
Demonstrates advanced features with **TARGET_PC support**:
- Inline C code for critical sections
- Direct hardware register access
- High-performance GPIO operations
- Mixed Python/C programming
- Cross-platform inline C code

**Compile for PC:**
```bash
py2mcu compile examples/demo3_inline_c.py --target pc -o build/
gcc build/demo3_inline_c.c -o build/demo3_inline_c
./build/demo3_inline_c
```

**Compile for STM32F4:**
```bash
py2mcu compile examples/demo3_inline_c.py --target stm32f4 -o build/
```

### demo4_memory.py - Memory Management
Demonstrates memory strategies:
- Stack allocation with `@static_alloc`
- Arena allocation with `@arena`
- Reference counting for persistent data
- Memory usage patterns

**Compile:**
```bash
py2mcu compile examples/demo4_memory.py --target pc -o build/
gcc build/demo4_memory.c runtime/gc_runtime.c -o build/demo4_memory
./build/demo4_memory
```

### demo5_docstring_c.py - Docstring Embedded C Code
Demonstrates docstring-embedded C code:
- Use `__C_CODE__` marker in function docstrings
- Python remains executable for PC testing
- C code compiled to MCU for performance
- Direct register access (GPIO, ADC, timers)
- Critical timing sections with inline assembly

**Key Feature:**
Functions with `__C_CODE__` in their docstring will have that C code compiled to the MCU, while the Python fallback code runs during PC testing.

**Example:**
```python
def gpio_toggle(pin: int) -> None:
    """__C_CODE__
    GPIOA->ODR ^= (1 << pin);
    """
    # Python fallback for PC testing
    print(f"Toggle pin {pin}")
```

**Compile:**
```bash
py2mcu compile examples/demo5_docstring_c.py --target stm32f4 -o build/
```

**Test on PC:**
```bash
python examples/demo5_docstring_c.py
```

### demo6_defines.py - C Preprocessor Defines
Demonstrates `@#define` comment annotations:
- Generate C `#define` directives from Python constants
- Hardware configuration constants with type hints
- Buffer sizes and compile-time limits
- Feature flags (boolean to 0/1)
- String constants
- Expression support (e.g., `1000 * 60`)

**Key Feature:**
Use `# @#define` comments to mark constants for C preprocessing. Supports optional type hints for type-safe constants.

**Example:**
```python
LED_PIN = 13  # @#define uint8_t
MAX_SAMPLES = 100  # @#define
TIMEOUT_MS = 1000 * 60  # @#define
DEBUG_ENABLED = True  # @#define
DEVICE_NAME = "py2mcu"  # @#define
```

**Generated C:**
```c
#define LED_PIN ((uint8_t)13)
#define MAX_SAMPLES 100
#define TIMEOUT_MS (1000 * 60)
#define DEBUG_ENABLED 1
#define DEVICE_NAME "py2mcu"
```

**Compile:**
```bash
py2mcu compile examples/demo6_defines.py --target stm32f4 -o build/
```

**Test on PC:**
```bash
python examples/demo6_defines.py
```
