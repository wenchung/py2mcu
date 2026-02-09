#!/usr/bin/env python3
"""
Demo 4: Memory Management Showcase
Demonstrates: Arena allocation, reference counting, scope management
"""

from py2mcu import arena, static_alloc

# Stack allocation for small fixed-size data
@static_alloc
def process_small_data() -> int:
    """Process small data using stack allocation
    
    __C_CODE__
    // Stack allocation for small buffer
    int32_t buffer[10];
    for (int i = 0; i < 10; i++) {
        buffer[i] = i * i;
    }
    
    // Calculate sum
    int32_t total = 0;
    for (int i = 0; i < 10; i++) {
        total += buffer[i];
    }
    return total;
    """
    buffer: list = [0] * 10  # Allocated on stack

    i: int = 0
    while i < 10:
        buffer[i] = i * i
        i = i + 1

    # Calculate sum
    total: int = 0
    i = 0
    while i < 10:
        total = total + buffer[i]
        i = i + 1

    return total  # buffer automatically freed

# Arena allocation for temporary data
@arena
def process_large_temp_data() -> int:
    """Process large temporary data using arena"""
    # These allocations come from arena and are freed together
    buffer1: list = [0] * 100
    buffer2: list = [0] * 100

    # Fill buffers
    i: int = 0
    while i < 100:
        buffer1[i] = i
        buffer2[i] = i * 2
        i = i + 1

    # Calculate result
    result: int = 0
    i = 0
    while i < 100:
        result = result + buffer1[i] + buffer2[i]
        i = i + 1

    return result
    # Arena automatically freed here

def create_persistent_data(size: int) -> list:
    """Create data that persists (reference counted)
    
    __C_CODE__
    // Allocate with reference counting
    int32_t* data = (int32_t*)malloc(size * sizeof(int32_t));
    if (data == NULL) return NULL;
    
    for (int i = 0; i < size; i++) {
        data[i] = i;
    }
    return data;
    """
    # Python: use list comprehension
    data: list = [0] * size

    i: int = 0
    while i < size:
        data[i] = i
        i = i + 1

    return data  # Caller owns the reference

def memory_stress_test() -> None:
    """Test different memory allocation strategies"""

    print("=== Memory Management Demo ===")

    # Test 1: Stack allocation
    print("Test 1: Stack allocation")
    result1: int = process_small_data()
    print("Result:", result1)

    # Test 2: Arena allocation
    print("Test 2: Arena allocation (temporary)")
    result2: int = process_large_temp_data()
    print("Result:", result2)

    # Test 3: Reference counting
    print("Test 3: Reference counting (persistent)")
    persistent: list = create_persistent_data(50)

    # Use persistent data
    sum: int = 0
    i: int = 0
    while i < 50:
        sum = sum + persistent[i]
        i = i + 1

    print("Persistent data sum:", sum)
    # persistent will be freed when function exits

def benchmark_allocators() -> None:
    """Benchmark different allocation strategies"""
    iterations: int = 100

    print("\n=== Allocation Benchmark ===")
    print("Iterations:", iterations)

    # Benchmark stack allocation
    print("Benchmarking stack allocation...")
    i: int = 0
    while i < iterations:
        result: int = process_small_data()
        i = i + 1
    print("Stack: Done")

    # Benchmark arena allocation
    print("Benchmarking arena allocation...")
    i = 0
    while i < iterations:
        result: int = process_large_temp_data()
        i = i + 1
    print("Arena: Done")

def main() -> None:
    """Main program"""
    memory_stress_test()
    benchmark_allocators()

    print("\n=== Demo Complete ===")
    print("Check memory statistics for details")

if __name__ == "__main__":
    main()