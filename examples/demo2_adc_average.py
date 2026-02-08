#!/usr/bin/env python3
"""
Demo 2: ADC Average - Array Processing
Demonstrates: arrays, loops, arithmetic
"""

# Configuration
ADC_PIN: int = 0
SAMPLE_COUNT: int = 10
SAMPLE_DELAY: int = 50  # milliseconds

def delay_ms(ms: int) -> None:
    """Delay for specified milliseconds"""
    pass

def adc_read(pin: int) -> int:
    """Read ADC value (0-4095 for 12-bit ADC)"""
    pass

def read_adc_samples(samples: list, count: int) -> None:
    """Read multiple ADC samples into array"""
    i: int = 0
    while i < count:
        samples[i] = adc_read(ADC_PIN)
        delay_ms(SAMPLE_DELAY)
        i = i + 1

def calculate_average(samples: list, count: int) -> int:
    """Calculate average of samples"""
    total: int = 0
    i: int = 0

    # Sum all samples
    while i < count:
        total = total + samples[i]
        i = i + 1

    # Return average
    return total // count  # Integer division

def find_min_max(samples: list, count: int) -> tuple:
    """Find minimum and maximum values"""
    min_val: int = samples[0]
    max_val: int = samples[0]
    i: int = 1

    while i < count:
        if samples[i] < min_val:
            min_val = samples[i]
        if samples[i] > max_val:
            max_val = samples[i]
        i = i + 1

    return (min_val, max_val)

def main() -> None:
    """Main program"""
    # Allocate sample buffer
    samples: list = [0] * SAMPLE_COUNT

    while True:
        # Read samples
        read_adc_samples(samples, SAMPLE_COUNT)

        # Calculate statistics
        avg: int = calculate_average(samples, SAMPLE_COUNT)
        min_max: tuple = find_min_max(samples, SAMPLE_COUNT)

        print("Average:", avg)
        print("Min:", min_max[0], "Max:", min_max[1])

        delay_ms(1000)

if __name__ == "__main__":
    main()
