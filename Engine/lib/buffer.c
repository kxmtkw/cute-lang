#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include "common/config.h"
#include "core/context.h"

#include "common/atom.h"
#include "common/error.h"

#include "objects/manager.h"
#include "objects/object.h"

#include "lib/buffer.h"

#include "utils/utils.h"


void
_ct_lib_buffer_too_large(uint64_t size) {
	CT_ERROR_LIB(
		ct_thread_error, 
		"Buffer", 
		"TooLarge", 
		"Buffer of size %u cannot be allocated. Exceeds the max size %lu (2GB).",
		size, CT_LIB_BUFFER_MAX_SIZE
	)
}


CtBufferObject*
ct_lib_buffer_new(CtObjectManager* manager, uint64_t size) {

	if (size > CT_LIB_BUFFER_MAX_SIZE) {
		_ct_lib_buffer_too_large(size);
		return NULL;
	}

	CtBufferObject* buffer = (CtBufferObject*) ct_objects_new_object(manager, sizeof(CtBufferObject), 1, ct_lib_buffer_del);

	if (!buffer) {
		return NULL;
	}

	buffer->size = size;
	buffer->capacity = size < 16 ? 16: size;
	buffer->data = (uint8_t*) malloc(buffer->capacity);

	if (!buffer->data) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"Allocation", 
			"Failed to allocate data (%u bytes) for buffer.",
			size
		)
		return NULL;
	}

	memset(buffer->data, 0, buffer->size);

	CT_LOG("lib/buffer", "Buffer [%p] of size %u bytes allocated.\n", buffer, size);
	
	return buffer;
}


bool
ct_lib_buffer_del(CtObjectManager* manager, CtObject* obj) {

	CtBufferObject* buffer = (CtBufferObject*) obj;

	if (buffer->data) free(buffer->data);
	buffer->data = NULL;
	buffer->size = 0;
	buffer->capacity = 0;

	CT_LOG("lib/buffer", "Freed data for Buffer [%p]\n", buffer);

	return true;
}


bool
ct_lib_buffer_resize(CtBufferObject* obj, uint64_t new_size) {

	if (new_size > CT_LIB_BUFFER_MAX_SIZE) {
		_ct_lib_buffer_too_large(new_size);
		return NULL;
	}

	if (new_size == obj->size) return true;

	if (new_size >= obj->capacity) {
		if (!ct_lib_buffer_reserve(obj, new_size)) {
			return false;
		}	

		memset(obj->data + obj->size, 0, new_size - obj->size);
	} 

	CT_LOG("lib/buffer", "Resized data for Buffer [%p] %u bytes -> %lu bytes.\n", obj, obj->size, new_size);

	obj->size = new_size;

	return true;
}


bool
ct_lib_buffer_reserve(CtBufferObject* obj, uint64_t new_cap) {

	if (new_cap > CT_LIB_BUFFER_MAX_SIZE) {
		_ct_lib_buffer_too_large(new_cap);
		return NULL;
	}

	if (new_cap <= obj->capacity) return true;

	uint8_t* data = realloc(obj->data, new_cap);

	if (!data) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"Allocation", 
			"Failed to allocate new memory (%u bytes -> %u bytes) for Buffer [%p].",
			obj->size, new_cap, obj
		)
		return false;
	}

	obj->data = data;

	CT_LOG("lib/buffer", "Reserved memory (%u bytes -> %lu bytes) for Buffer [%p].\n", obj->capacity, new_cap, obj);
	
	obj->capacity = new_cap;

	return true;
}


bool
ct_lib_buffer_truncate(CtBufferObject* obj) {

	uint8_t* data = realloc(obj->data, obj->size);

	uint32_t old_cap = obj->capacity;
	obj->data = data;
	obj->capacity = obj->size;

	CT_LOG("lib/buffer", "Truncated (%u bytes -> %u bytes) Buffer [%p] to fit.\n", old_cap, obj->capacity, obj);

	return true;
}


bool
ct_lib_buffer_get_byte(CtBufferObject* obj, uint32_t index, uint8_t* out) {

	if (index >= obj->size) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"OutOfRange",
			"Index %u falls out of range [0-%u]",
			index, obj->size-1
		)
		return false;
	}

	*out = obj->data[index];

	return true;
}


bool
ct_lib_buffer_set_byte(CtBufferObject* obj, uint32_t index, uint8_t byte) {

	if (index >= obj->size) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"OutOfRange",
			"Index %u falls out of range [0-%u]",
			index, obj->size-1
		);
		return false;
	}

	obj->data[index] = byte;
	return true;
}

bool
ct_lib_buffer_set_bytes(CtBufferObject* obj, uint32_t index, uint8_t* bytes, uint32_t count) {

	// if say index is 0, count is 4, then 0+4 is 4 but the actual data is only upto index 3 count(0,1,2,3) = 4
	// hence the -1 which is also equivalent to converting >= to >

	if (index + count - 1 >= obj->size) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"OutOfRange",
			"Range [%u-%u] falls out of range [0-%u]",
			index, index + count - 1, obj->size-1
		)
		return false;
	}

	memcpy(&obj->data[index], bytes, count);
	return true;
}


bool
ct_lib_buffer_set_buffer(CtBufferObject* obj, uint32_t index, CtBufferObject* other) {

	if (!ct_lib_buffer_set_bytes(obj, index, other->data, other->size)) {
		return false;
	}

	CT_LOG("lib/buffer", "Set Buffer [%p] data to Buffer [%p] starting from index %u.\n", obj, other, index);

	return true;
}


static inline bool
_ct_lib_buffer_reserve_if_required(CtBufferObject* obj) {

	// Keeping reserving until we can finally fit size. This is done so push_bytes and append_buffer can
	// intake any number of bytes. 

	while (obj->size >= obj->capacity) {
		
		uint32_t new_cap = obj->capacity + (obj->capacity >> 1);

		if (!ct_lib_buffer_reserve(obj, new_cap)) {
			return false;
		}
	}

	return true;
}

bool
ct_lib_buffer_push_byte(CtBufferObject* obj, uint8_t byte) {

	obj->size++;

	if (!_ct_lib_buffer_reserve_if_required(obj)) {
		return false;
	}

	obj->data[obj->size] = byte;
	return true;
}


bool
ct_lib_buffer_push_bytes(CtBufferObject* obj, uint8_t* byte, uint32_t count) {
	
	uint32_t old_size = obj->size;
	obj->size += count;

	if (!_ct_lib_buffer_reserve_if_required(obj)) {
		return false;
	}

	memcpy(obj->data + old_size, byte, count);
}


bool
ct_lib_buffer_append_buffer(CtBufferObject* obj, CtBufferObject* other) {

	if (obj == other) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"SelfAppend",
			"Cannot append buffer to itself.",
			NULL
		)
		return false;
	}

	if (!ct_lib_buffer_push_bytes(obj, other->data, other->size)) {
		return false;
	}

	CT_LOG("lib/buffer", "Appended Buffer [%p] to Buffer [%p]\n", other, obj);

	return true;
}


CtBufferObject*
ct_lib_buffer_slice(CtBufferObject* obj, uint32_t index, uint32_t length) {

	if (index + length > obj->size) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"OutOfRange",
			"Range [%u-%u] falls out of range [0-%u]",
			index, index + length
		)
		return NULL;
	}

	CtBufferObject* slice = ct_lib_buffer_new(obj->__object__.manager, length);

	memcpy(slice->data, &obj->data[index], slice->size);

	CT_LOG("lib/buffer", "Sliced Buffer [%p] from Buffer [%p] with range [%u-%u]\n", slice, obj, index, index + length);
	
	return slice;

}


CtBufferObject*
ct_lib_buffer_copy(CtBufferObject* obj) {

	CtBufferObject* buffer_copy = ct_lib_buffer_new(obj->__object__.manager, obj->size);
	
	if (!buffer_copy) {
		return NULL;
	}
	
	memcpy(buffer_copy->data, obj->data, obj->size);

	CT_LOG("lib/buffer", "Copied Buffer [%p] from Buffer [%p].\n", buffer_copy, obj);

	return buffer_copy;

}


bool
ct_lib_buffer_fill(CtBufferObject* obj, uint8_t byte) {

	memset(obj->data, byte, obj->size);

	CT_LOG("lib/buffer", "Set Buffer [%p] data to %u.\n", obj, byte);

	return true;
}


bool
ct_lib_buffer_clear(CtBufferObject* obj) {

	memset(obj->data, 0, obj->size);
	
	CT_LOG("lib/buffer", "Cleared Buffer [%p]\n", obj);

	return true;
}


bool
ct_lib_buffer_find_byte(CtBufferObject* obj, uint8_t byte, uint32_t start_idx, uint32_t* out) {

	if (start_idx >= obj->size) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"OutOfRange",
			"Starting index %u is greater than Buffer size %u.",
			start_idx, obj->size
		)
		return false;
	}

	
	CT_LOG("lib/buffer", "Finding byte %u/%c/0x%x in Buffer [%p].\n", byte, byte, byte, obj);

	for (uint32_t i = start_idx; i < obj->size; i++) {
		if (obj->data[i] == byte) {
			*out = i;
			return true;
		}
	}

	*out = UINT32_MAX;
	return true;
}


bool
ct_lib_buffer_find_bytes(CtBufferObject* obj, uint8_t* bytes, uint32_t count, uint32_t start_idx, uint32_t* out) {

	if (start_idx + count >= obj->size) {
		CT_ERROR_LIB(
			ct_thread_error, 
			"Buffer", 
			"OutOfRange",
			"Byte pattern of size %u cannot be searched from starting index %u in Buffer of size %u.",
			count, start_idx, obj->size
		)
		return false;
	}

	bool found = false;

	for (uint32_t i = start_idx; i + count - 1 < obj->size; i++) {

		for (uint32_t j = 0; j < count; j++) {

			if (obj->data[i+j] != bytes[j]) {
				found = false;
				break;
			} else {
				found = true;
			}

		}

		if (found) {
			*out = i;
			return true;
		}
	}

	*out = UINT32_MAX;
	return true;
}


bool
ct_lib_buffer_find_buffer(CtBufferObject* obj, CtBufferObject* other, uint32_t start_idx, uint32_t* out) {
	return ct_lib_buffer_find_bytes(obj, other->data, other->size, start_idx, out);
}


bool
ct_lib_buffer_equals(CtBufferObject* obj, CtBufferObject* other, bool* out) {
	
	if (obj == other) {
		*out = true;
		return true;
	}
	
	if (obj->size != other->size) {
		*out = false;
		return true;
	}

	for (uint32_t i = 0; i < obj->size; i++) {
		if (obj->data[i] != other->data[i]) {
			*out = false;
			return true;
		}
	}

	*out = true;
	return true;
}