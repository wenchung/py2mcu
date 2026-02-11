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

### Important Notes

- **Always use type annotations**: Python requires explicit types for all variables and function returns
- **No type inference**: Unlike modern C++, py2mcu does not auto-deduce types from assignments
- **Match MCU abilities**: Use `uint8_t`/`int8_t` for 8-bit MCUs, `int32_t` for 32-bit addressing



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

py2mcu unifies MCU and PC code through target macros:

### Target Macros

| Macro | Description |
|---------------|-------------|
| `TARGET_PC` | Compiling for PC |
| `TARGETS_HARDWARE` | Compiling for any MCU (STM32, ESP32, etc.) |
| `TARGET_STM32` | Specific to STM32 chips |
| `TARGET_ESP32` | Specific to ESP32 chips |
| `TARGET_RP2040` | Specific to Raspberry Pi Pico |

### Example: Platform-Specific Code

```python
def get_adc_value() -> uint8_t:
    result: uint8_t = 0
    
    __C_CODE__ = """
    #ifdef TARGET_PC
        // Simulate ADC: return random value
        result = rand() % 256;
    #elif defined(TARGET_STM32)
        // Real HAL call for STM32
        result = HAL_ADC_GetValue(&hadc1) & 0xFF;
    #else
        #error "Unsupported target"
    #endif
    """
    
    return result
```

## Inline C Code

Write performance-critical or hardware-specific code directly in C using `__C_CODE__` string literals:

```python
def blink_led() -> None:
    delay_time: uint32_t = 500
    
    __C_CODE__ = """
    #ifdef TARGET_STM32
        HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    #elif defined(TARGET_ESP32)
        gpio_set_level(LED_PIN, 1);
    #else
        printf("LED ON (PC simulation)\n");
    #endif
    
    #ifdef TARGET_PC
        usleep(delay_time * 1000);
    #else
        HAL_Delay(delay_time);
    #endif
    """
```

## Examples

See `examples/` for more:

- `demo1_led_blink.py` - Basic GPIO control
```