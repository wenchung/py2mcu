# py2mcu Examples

This directory contains example programs demonstrating py2mcu features.

## Demo Programs

### demo1_led_blink.py - Basic Control Flow
Demonstrates fundamental concepts:
- Function definitions with type annotations
- While loops and conditionals
- Basic GPIO operations
- Platform-independent delay

**Compile:**
```bash
py2mcu compile examples/demo1_led_blink.py --target stm32f4 -o build/
```

### demo2_adc_average.py - Array Processing
Demonstrates data processing:
- Fixed-size arrays
- For/while loops with arrays
- Integer arithmetic and division
- Sensor data processing patterns

**Compile:**
```bash
py2mcu compile examples/demo2_adc_average.py --target stm32f4 -o build/
```

### demo3_inline_c.py - Performance Optimization
Demonstrates advanced features:
- Inline C code for critical sections
- Direct hardware register access
- High-performance GPIO operations
- Mixed Python/C programming

**Compile:**
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

## Generated C Code

After compilation, check the `build/` directory for generated C code.

Example output structure:
```
build/
├── demo1_led_blink.c
├── demo2_adc_average.c
├── demo3_inline_c.c
└── demo4_memory.c
```

## Testing on PC

Test your code on PC before deploying to MCU:

```bash
# Compile for PC
py2mcu compile examples/demo4_memory.py --target pc -o build/

# Compile and link with GC runtime
gcc build/demo4_memory.c runtime/gc_runtime.c -o build/demo4_memory -I runtime/

# Run
./build/demo4_memory
```

## Deploying to MCU

```bash
# For STM32F4
py2mcu deploy examples/demo1_led_blink.py --target stm32f4 --port /dev/ttyUSB0

# For ESP32
py2mcu deploy examples/demo1_led_blink.py --target esp32 --port /dev/ttyUSB0
```

## Notes

- All demos use type annotations (Python 3.5+)
- Hardware-specific code is abstracted through function calls
- Generated C code is optimized for size and speed
- Memory management is handled automatically based on usage patterns
