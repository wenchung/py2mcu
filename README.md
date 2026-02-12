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

## 💚 Support This Project

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
|-------------------|--------|-------|
| `uint8_t` | `uint8_t` | 0 ~ 255 |
| `uint16_t` | `uint16_t` | 0 ~ 65535 |
| `uint32_t` | `uint32_t` | 0 ~ 4294967295 |
| `int8_t` | `int8_t` | -128 ~ 127 |
| `int16_t` | `int16_t` | -32768 ~ 32767 |
| `int32_t` | `int32_t` | -2147483648 ~ 2147483647 |

### Type Inference

If you don't specify a type, py2mcu will infer it from the initial value (default to `int`):

```python
def type_example() -> None:
    # Inferred as 'int'
    
    count = 10          # integer
    value = 0x4200      # hexadecimal integer
    mask = 0x7F         # bit mask (int)
```

## Volatile Variables

For hardware registers or variables modified by interrupts/DMA, use the `# @volatile` comment to mark variables as `volatile` in generated C code:

### Example: Hardware Register Access

```python
def read_sensor() -> None:
    sensor_value: uint16_t = 0  # @volatile
    
    __C_CODE__ = """
    #ifdef TARGET_PC
        sensor_value = rand() % 1024;
    #else
        sensor_value = *((volatile uint16_t*)SENSOR_REG_ADDR);
    #endif
    """
```

### Generated C Code

```c
volatile uint16_t sensor_value = 0;  // volatile keyword added automatically
```

### When to Use @volatile

- **Hardware registers**: Memory-mapped I/O that hardware can modify
- **Interrupt handlers**: Variables shared between ISRs and main code
- **DMA buffers**: Memory modified by DMA controllers
- **Multi-threaded access**: Variables accessed by multiple threads (RTOS)

The `# @volatile` comment prevents compiler optimizations that assume the variable's value only changes through explicit assignments in your code.

## Cross-Platform Development

py2mcu provides Platform-specific macros to control code generation for different targets. You can define these macros in three ways:

### Method 1: Compiler flags

```bash
# For PC simulation (matches --target pc)
gcc -DTARGET_PC main.c -o main

# For STM32 (matches --target stm32)
arm-none-eabi-gcc -DTARGET_STM32 -DTARGETS_HARDWARE main.c -o main.elf

# For ESP32 (matches --target esp32)
xtensa-esp32-elf-gcc -DTARGET_ESP32 -DTARGETS_HARDWARE main.c -o main.elf
```

### Method 2: Project Configuration

For CMake or Makefile projects, define target macros in your build files:

```cmake
# CmakeLists.txt
add_definitions(-DTARGET_STM32)
add_definitions(-DTARGETS_HARDWARE)
```

### Method 3: Using py2mcu CLI

```bash
# Command line uses lowercase (easier to type)
py2mcu compile --target pc input.py
py2mcu compile --target stm32 input.py
py2mcu compile --target esp32 input.py

# Automatically generates uppercase macros (C convention)
# --target pc     → #define TARGET_PC 1
# --target stm32  → #define TARGET_STM32 1
# --target esp32  → #define TARGET_ESP32 1
```

### Available Macros

#### Platform Macros

| Macro | Description | CLI Flag |
|-------|-------------|----------|
| `TARGET_PC` = 1 | PC simulation | `--target pc` |
| `TARGET_STM32` = 1 | STM32 microcontrollers | `--target stm32` |
| `TARGET_ESP32` = 1 | ESP32 microcontrollers | `--target esp32` |
| `TARGET_RP2040` = 1 | Raspberry Pi Pico | `--target rp2040` |
| `TARGETS_HARDWARE` = 1 | Any hardware target (not PC) | auto-set for MCU targets |

### Platform-Specific Macros

**PC Target:**
```bash
py2mcu compile --target pc input.py
```
Generates:
```c
#define TARGET_PC 1
```

**STM32 Target:**
```bash
py2mcu compile --target stm32 input.py
```
Generates:
```c
#define TARGET_STM32 1
#define TARGETS_HARDWARE 1
```

**ESP32 Target:**
```bash
py2mcu compile --target esp32 input.py
```
Generates:
```c
#define TARGET_ESP32 1
#define TARGETS_HARDWARE 1
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

See [LICENSE_DUAL.md](LICENSE_DUAL.md) for details.
