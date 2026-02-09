#!/usr/bin/env python3
"""
Demo 2: ADC Sampling and Average Calculation
Demonstrates: arrays, for loops, arithmetic operations
"""

# Configuration
SAMPLE_SIZE: int = 10
ADC_CHANNEL: int = 0
THRESHOLD: int = 512

def read_adc(channel: int) -> int:
    """Read ADC value (0-1023)
    
    __C_CODE__
    // STM32F4 ADC read (12-bit resolution)
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = ADC_CHANNEL_0 + channel;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_15CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 100);
    uint32_t value = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    
    return value;
    """
    # PC simulation: random value
    import random
    return random.randint(0, 1023)

def gpio_write(pin: int, value: bool) -> None:
    """Write to GPIO
    
    __C_CODE__
    // STM32F4 GPIO control
    if (value) {
        GPIOA->BSRR = (1 << pin);
    } else {
        GPIOA->BSRR = (1 << (pin + 16));
    }
    """
    # PC simulation
    print(f"GPIO {pin}: {'ON' if value else 'OFF'}")

def calculate_average(samples: list, size: int) -> int:
    """Calculate average of samples"""
    total: int = 0
    i: int = 0

    while i < size:
        total = total + samples[i]
        i = i + 1

    return total // size  # Integer division

def collect_samples() -> list:
    """Collect ADC samples"""
    samples: list = [0] * SAMPLE_SIZE
    i: int = 0

    while i < SAMPLE_SIZE:
        samples[i] = read_adc(ADC_CHANNEL)
        i = i + 1

    return samples

def process_sensor_data() -> None:
    """Read sensors and make decision"""
    # Collect samples
    samples: list = collect_samples()

    # Calculate average
    avg: int = calculate_average(samples, SAMPLE_SIZE)

    # Make decision based on threshold
    if avg > THRESHOLD:
        gpio_write(13, True)   # Turn on LED
        print("Average high:", avg)
    else:
        gpio_write(13, False)  # Turn off LED
        print("Average low:", avg)

def main() -> None:
    """Main program"""
    print("ADC Average Demo")
    print("Sample size:", SAMPLE_SIZE)
    print("Threshold:", THRESHOLD)

    while True:
        process_sensor_data()
        # delay_ms(1000)

if __name__ == "__main__":
    main()