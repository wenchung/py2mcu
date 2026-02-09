#!/usr/bin/env python3
"""
Demo 3: Inline C for Performance-Critical Code
Demonstrates: inline C integration, direct hardware access
"""

from py2mcu import inline_c

# For STM32F4, direct register access
INLINE_GPIO_CODE = """
// Fast GPIO operations using direct register access
#define GPIOC_BASE 0x40020800
#define GPIO_BSRR_OFFSET 0x18
#define GPIO_IDR_OFFSET 0x10

static inline void fast_gpio_set(int pin, int value) {
    volatile uint32_t* bsrr = (uint32_t*)(GPIOC_BASE + GPIO_BSRR_OFFSET);
    if (value) {
        *bsrr = (1 << pin);           // Set bit
    } else {
        *bsrr = (1 << (pin + 16));    // Reset bit
    }
}

static inline uint32_t fast_gpio_read(int pin) {
    volatile uint32_t* idr = (uint32_t*)(GPIOC_BASE + GPIO_IDR_OFFSET);
    return (*idr >> pin) & 1;
}
"""

@inline_c(INLINE_GPIO_CODE)
def gpio_set_fast(pin: int, value: bool) -> None:
    """Fast GPIO write using inline C
    
    Alternative with __C_CODE__ marker:
    __C_CODE__
    volatile uint32_t* bsrr = (uint32_t*)(0x40020800 + 0x18);
    if (value) {
        *bsrr = (1 << pin);
    } else {
        *bsrr = (1 << (pin + 16));
    }
    """
    fast_gpio_set(pin, 1 if value else 0)

@inline_c(INLINE_GPIO_CODE)
def gpio_read_fast(pin: int) -> int:
    """Fast GPIO read using inline C
    
    Alternative with __C_CODE__ marker:
    __C_CODE__
    volatile uint32_t* idr = (uint32_t*)(0x40020800 + 0x10);
    return (*idr >> pin) & 1;
    """
    return fast_gpio_read(pin)

def critical_timing_loop() -> None:
    """Time-critical loop using inline C for performance"""
    count: int = 0

    while count < 1000000:
        # These calls compile to direct register access
        gpio_set_fast(13, True)
        gpio_set_fast(13, False)
        count = count + 1

def button_debounce(pin: int) -> bool:
    """Debounce button using fast GPIO reads"""
    # Read button state 5 times
    readings: int = 0
    i: int = 0

    while i < 5:
        state: int = gpio_read_fast(pin)
        readings = readings + state
        i = i + 1

    # Button is pressed if majority reads are high
    return readings >= 3

def main() -> None:
    """Main program"""
    print("Inline C Demo")
    print("Running critical timing loop...")

    critical_timing_loop()

    print("Testing button debounce...")
    button_pin: int = 0

    while True:
        if button_debounce(button_pin):
            print("Button pressed!")
            gpio_set_fast(13, True)
        else:
            gpio_set_fast(13, False)

if __name__ == "__main__":
    main()