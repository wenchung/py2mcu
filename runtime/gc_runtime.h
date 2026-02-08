#ifndef GC_RUNTIME_H
#define GC_RUNTIME_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// ============ Configuration ============
#define GC_ARENA_SIZE 16384
#define GC_USE_REFCOUNT 1

// ============ Arena Allocator ============
typedef struct {
    uint8_t* memory;
    size_t size;
    size_t offset;
} gc_arena_t;

void gc_arena_init(gc_arena_t* arena, void* buffer, size_t size);
void* gc_arena_alloc(gc_arena_t* arena, size_t size);
void gc_arena_reset(gc_arena_t* arena);
size_t gc_arena_checkpoint(gc_arena_t* arena);
void gc_arena_restore(gc_arena_t* arena, size_t checkpoint);

// Global arena
extern gc_arena_t global_arena;

// ============ Reference Counting ============
#if GC_USE_REFCOUNT
typedef struct {
    uint32_t refcount;
    uint32_t size;
    uint8_t data[];
} gc_object_t;

void* gc_alloc(size_t size);
void* gc_retain(void* ptr);
void gc_release(void* ptr);
uint32_t gc_refcount(void* ptr);
#endif

// ============ Statistics ============
typedef struct {
    size_t total_allocated;
    size_t current_used;
    size_t peak_used;
    uint32_t alloc_count;
    uint32_t free_count;
} gc_stats_t;

void gc_get_stats(gc_stats_t* stats);
void gc_print_stats(void);

// ============ Helper Macros ============
#define GC_SCOPE_START() size_t __gc_cp = gc_arena_checkpoint(&global_arena)
#define GC_SCOPE_END() gc_arena_restore(&global_arena, __gc_cp)

#endif
