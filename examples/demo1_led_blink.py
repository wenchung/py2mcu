#!/usr/bin/env python3
"""
Demo 1: LED Blink - Basic Control Flow
Demonstrates: if/while loops, function calls, basic GPIO
"""

# Hardware configuration
LED_PIN: int = 13
BLINK_DELAY: int = 500  # milliseconds

def delay_ms(ms: int) -> None:
    """Delay for specified milliseconds
    
    __C_CODE__
    // STM32F4 precise delay using SysTick
    uint32_t start = HAL_GetTick();
    while ((HAL_GetTick() - start) < ms) {
        __NOP();  // No operation, just wait
    }
    """
    # PC simulation: Python sleep
    import time
    time.sleep(ms / 1000.0)

def gpio_write(pin: int, value: bool) -> None:
    """Write digital value to GPIO pin
    
    __C_CODE__
    // STM32F4 GPIO write (assumes GPIOA)
    if (value) {
        GPIOA->BSRR = (1 << pin);  // Set pin high
    } else {
        GPIOA->BSRR = (1 << (pin + 16));  // Set pin low
    }
    """
    # PC simulation: print GPIO state
    print(f"GPIO Pin {pin}: {'HIGH' if value else 'LOW'}")

def setup() -> None:
    """Initialize hardware"""
    # Configure LED pin as output
    print("Setting up LED on pin", LED_PIN)

def blink_led(times: int) -> None:
    """Blink LED specified number of times"""
    count: int = 0
    while count < times:
        gpio_write(LED_PIN, True)   # LED on
        delay_ms(BLINK_DELAY)
        gpio_write(LED_PIN, False)  # LED off
        delay_ms(BLINK_DELAY)
        count = count + 1

def main() -> None:
    """Main program"""
    setup()

    # Blink LED forever
    while True:
        blink_led(3)       # Quick blinks
        delay_ms(2000)     # Long pause

if __name__ == "__main__":
    main()