#!/usr/bin/env python3
"""
Demo 3: Inline C - Performance Optimization
Demonstrates: inline C code, direct hardware access
"""

from py2mcu.decorators import inline_c

# Hardware configuration (STM32F4 example)
GPIOA_BASE: int = 0x40020000
GPIO_ODR_OFFSET: int = 0x14

@inline_c("""
// Fast GPIO toggle using direct register access
void gpio_toggle_fast(uint32_t gpio_base, uint8_t pin) {
    volatile uint32_t* odr = (uint32_t*)(gpio_base + 0x14);
    *odr ^= (1 << pin);
}
""")
def gpio_toggle(gpio_base: int, pin: int) -> None:
    """Toggle GPIO pin using inline C"""
    # This Python code is replaced by inline C at compile time
    pass

@inline_c("""
// Fast delay using assembly NOP instructions
void delay_cycles(uint32_t cycles) {
    while(cycles--) {
        __asm__ volatile("nop");
    }
}
""")
def delay_cycles(cycles: int) -> None:
    """Precise delay in CPU cycles"""
    pass

def delay_ms(ms: int) -> None:
    """Standard delay"""
    pass

def benchmark_gpio() -> None:
    """Benchmark GPIO performance"""
    pin: int = 5
    iterations: int = 10000
    i: int = 0

    print("Starting GPIO benchmark...")

    # Fast toggle using inline C
    while i < iterations:
        gpio_toggle(GPIOA_BASE, pin)
        delay_cycles(100)
        i = i + 1

    print("Benchmark complete")

def pulse_train(pin: int, pulse_count: int, period_cycles: int) -> None:
    """
    Generate precise pulse train
    Uses inline C for timing-critical code
    """
    count: int = 0
    while count < pulse_count:
        gpio_toggle(GPIOA_BASE, pin)  # High
        delay_cycles(period_cycles // 2)
        gpio_toggle(GPIOA_BASE, pin)  # Low
        delay_cycles(period_cycles // 2)
        count = count + 1

def main() -> None:
    """Main program"""
    print("Inline C Performance Demo")

    # Run benchmark
    benchmark_gpio()

    # Generate 1000 pulses at ~1MHz (assuming 168MHz CPU)
    pulse_train(5, 1000, 168)

    print("Demo complete")

if __name__ == "__main__":
    main()
