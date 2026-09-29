#ifndef CT_LIB_BUFFER_H
#define CT_LIB_BUFFER_H

#include "common/atom.h"
#include "common/error.h"

#include "objects/object.h"


typedef struct {
	CtObject __object__;
	uint8_t* data;
	uint32_t size;
	uint32_t capacity;
} CtBufferObject;

#define CT_LIB_BUFFER_MAX_SIZE (INT32_MAX)

// Create a new buffer with the given size.
CtBufferObject*
ct_lib_buffer_new(CtObjectManager* manager, uint64_t size);

// Delete method for the buffer object.
bool
ct_lib_buffer_del(CtObjectManager* manager, CtObject* obj);

// Resize a buffer. Truncates data if new size is less.
bool
ct_lib_buffer_resize(CtBufferObject* obj, uint64_t new_size);

// Reserve data for a buffer, skips if new cap is less then current cap.
bool
ct_lib_buffer_reserve(CtBufferObject* obj, uint64_t new_cap);

// Truncates the current capacity to fit the size.
bool
ct_lib_buffer_truncate(CtBufferObject* obj);

// Get a byte at a specific index in the buffer
bool
ct_lib_buffer_get_byte(CtBufferObject* obj, uint32_t index, uint8_t* out);

// Set a byte at a specific index in the buffer.
bool
ct_lib_buffer_set_byte(CtBufferObject* obj, uint32_t index, uint8_t byte);

// Set n bytes starting from index.
// #INTERNAL
bool
ct_lib_buffer_set_bytes(CtBufferObject* obj, uint32_t index, uint8_t* bytes, uint32_t count);

// Set the buffer's data with another buffer starting from index. Fails if first buffer is too small
bool
ct_lib_buffer_set_buffer(CtBufferObject* obj, uint32_t index, CtBufferObject* other);

// Push a byte to the end of the buffer.
bool
ct_lib_buffer_push_byte(CtBufferObject* obj, uint8_t byte);

// Push a byte to the end of the buffer.
bool
ct_lib_buffer_push_bytes(CtBufferObject* obj, uint8_t* byte, uint32_t count);

// Push a buffer to the end of the buffer.
bool
ct_lib_buffer_append_buffer(CtBufferObject* obj, CtBufferObject* other);

// Get a slice from the buffer
CtBufferObject*
ct_lib_buffer_slice(CtBufferObject* obj, uint32_t index, uint32_t length);

// Create a copy of a buffer.
CtBufferObject*
ct_lib_buffer_copy(CtBufferObject* obj);

// Sets every byte in the buffer to a specific value.
bool
ct_lib_buffer_fill(CtBufferObject* obj, uint8_t byte);

// Clears the data for a buffer. Sets everything to zero.
bool
ct_lib_buffer_clear(CtBufferObject* obj);

// Find a byte in the buffer. Returns the first index found.
bool
ct_lib_buffer_find_byte(CtBufferObject* obj, uint8_t byte, uint32_t start_idx, uint32_t* out);

// Find a byte pattern in the buffer. Returns the first index found.
bool
ct_lib_buffer_find_bytes(CtBufferObject* obj, uint8_t* byte, uint32_t count, uint32_t start_idx, uint32_t* out);

// Find a buffer pattern in the buffer. Returns the first index found.
bool
ct_lib_buffer_find_buffer(CtBufferObject* obj, CtBufferObject* other, uint32_t start_idx, uint32_t* out);

// Check if two buffers are equal
bool
ct_lib_buffer_equals(CtBufferObject* obj, CtBufferObject* other, bool* out);

#endif // CT_LIB_BUFFER_H