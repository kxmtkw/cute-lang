#ifndef CT_MODULE_BUFFER_H
#define CT_MODULE_BUFFER_H

#include <stdint.h>

#include "common/atom.h"
#include "common/error.h"
#include "core/context.h"
#include "modules/modulespec.h"


CT_MODULE_NAME_DEFINE(buffer, "Buffer");

#include "lib/buffer.h"

// 0: new
static void
ct_module_buffer_new(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_PRIMIT_ARG(0, uint32_t, size, as_uint);

    CtBufferObject* buffer = ct_lib_buffer_new(ct_ctx_get_object_manager(args.context), size);
	
    CT_MODCALL_RESULT(as_object, (CtObject*)buffer, CT_ATOM_OBJECT);
}


// 1: size
static void
ct_module_buffer_size(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_RESULT(as_uint, buffer->size, CT_ATOM_PRIMITIVE);
}


// 2: capacity
static void
ct_module_buffer_capacity(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    
    CT_MODCALL_RESULT(as_uint, buffer->capacity, CT_ATOM_PRIMITIVE);
}

// 3: resize
static void
ct_module_buffer_resize(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, new_size, as_uint);
    
    ct_lib_buffer_resize(buffer, new_size);
}

// 4: reserve
static void
ct_module_buffer_reserve(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, new_cap, as_uint);

    ct_lib_buffer_reserve(buffer, new_cap);
}

// 5: truncate
static void
ct_module_buffer_truncate(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));


    ct_lib_buffer_truncate(buffer);
}

// 6: get
static void
ct_module_buffer_get(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, index, as_uint);

    uint8_t byte_val = 0;
    if (ct_lib_buffer_get_byte(buffer, index, &byte_val)) {
        CT_MODCALL_RESULT(as_uint, (uint32_t)byte_val, CT_ATOM_PRIMITIVE);
    }
}

// 7: set
static void
ct_module_buffer_set(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, index, as_uint);
    CT_MODCALL_PRIMIT_ARG(2, uint32_t, byte_val, as_uint);

    ct_lib_buffer_set_byte(buffer, index, (uint8_t)byte_val);
}

// 8: set-buffer
static void
ct_module_buffer_set_buffer(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, dst);
	CT_MODCALL_OBJECT_TYPE_CHECK(dst, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, index, as_uint);
    CT_MODCALL_OBJECT_ARG(2, CtBufferObject*, src);
	CT_MODCALL_OBJECT_TYPE_CHECK(src, 1, CT_MODULE_NAME(buffer));

    if (ct_lib_buffer_set_buffer(dst, index, src)) {
        uint32_t written_upto = index + src->size;
        CT_MODCALL_RESULT(as_uint, written_upto, CT_ATOM_PRIMITIVE);
    }
}

// 9: push
static void
ct_module_buffer_push(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, byte_val, as_uint);

    ct_lib_buffer_push_byte(buffer, (uint8_t)byte_val);
}

// 10: append
static void
ct_module_buffer_append(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, dst);
	CT_MODCALL_OBJECT_TYPE_CHECK(dst, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_OBJECT_ARG(1, CtBufferObject*, src);
	CT_MODCALL_OBJECT_TYPE_CHECK(src, 1, CT_MODULE_NAME(buffer));

    ct_lib_buffer_append_buffer(dst, src);
}

// 11: slice
static void
ct_module_buffer_slice(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, index, as_uint);
    CT_MODCALL_PRIMIT_ARG(2, uint32_t, length, as_uint);

    CtBufferObject* sliced = ct_lib_buffer_slice(buffer, index, length);
    if (sliced != NULL) {
        CT_MODCALL_RESULT(as_object, (CtObject*)sliced, CT_ATOM_OBJECT);
    }
}

// 12: copy
static void
ct_module_buffer_copy(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));


    CtBufferObject* copied = ct_lib_buffer_copy(buffer);
    if (copied != NULL) {
        CT_MODCALL_RESULT(as_object, (CtObject*)copied, CT_ATOM_OBJECT);
    }
}

// 13: fill
static void
ct_module_buffer_fill(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, byte_val, as_uint);

    ct_lib_buffer_fill(buffer, (uint8_t)byte_val);
}

// 14: clear
static void
ct_module_buffer_clear(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));


    ct_lib_buffer_clear(buffer);
}

// 15: find-byte
static void
ct_module_buffer_find_byte(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, start_idx, as_uint);
    CT_MODCALL_PRIMIT_ARG(2, uint32_t, byte_val, as_uint);

    uint32_t found_idx = UINT32_MAX;
    if (ct_lib_buffer_find_byte(buffer, (uint8_t)byte_val, start_idx, &found_idx)) {
        CT_MODCALL_RESULT(as_uint, found_idx, CT_ATOM_PRIMITIVE);
    } else {
        CT_MODCALL_RESULT(as_uint, UINT32_MAX, CT_ATOM_PRIMITIVE);
    }
}

// 16: find-buffer
static void
ct_module_buffer_find_buffer(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_PRIMIT_ARG(1, uint32_t, start_idx, as_uint);
    CT_MODCALL_OBJECT_ARG(2, CtBufferObject*, sub_buffer);
	CT_MODCALL_OBJECT_TYPE_CHECK(sub_buffer, 1, CT_MODULE_NAME(buffer));

    uint32_t found_idx = UINT32_MAX;
    if (ct_lib_buffer_find_buffer(buffer, sub_buffer, start_idx, &found_idx)) {
        CT_MODCALL_RESULT(as_uint, found_idx, CT_ATOM_PRIMITIVE);
    } else {
        CT_MODCALL_RESULT(as_uint, UINT32_MAX, CT_ATOM_PRIMITIVE);
    }
}

// 17: equals
static void
ct_module_buffer_equals(CtModuleMethodArguments args, CtModuleMethodResult* result) {

    CT_MODCALL_OBJECT_ARG(0, CtBufferObject*, buffer_a);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer_a, 1, CT_MODULE_NAME(buffer));

    CT_MODCALL_OBJECT_ARG(1, CtBufferObject*, buffer_b);
	CT_MODCALL_OBJECT_TYPE_CHECK(buffer_b, 1, CT_MODULE_NAME(buffer));

    bool is_equal = false;
    if (ct_lib_buffer_equals(buffer_a, buffer_b, &is_equal)) {
        CT_MODCALL_RESULT(as_bool, is_equal, CT_ATOM_PRIMITIVE);
    }
}

CT_MODULE_METHOD_MAP_DEFINE(buffer) = {
    [0]  = CT_MODULE_ENTRY("new",         ct_module_buffer_new,         1),
    [1]  = CT_MODULE_ENTRY("size",        ct_module_buffer_size,        1),
    [2]  = CT_MODULE_ENTRY("capacity",    ct_module_buffer_capacity,    1),
    [3]  = CT_MODULE_ENTRY("resize",      ct_module_buffer_resize,      2),
    [4]  = CT_MODULE_ENTRY("reserve",     ct_module_buffer_reserve,     2),
    [5]  = CT_MODULE_ENTRY("truncate",    ct_module_buffer_truncate,    1),
    [6]  = CT_MODULE_ENTRY("get",         ct_module_buffer_get,         2),
    [7]  = CT_MODULE_ENTRY("set",         ct_module_buffer_set,         3),
    [8]  = CT_MODULE_ENTRY("set-buffer",  ct_module_buffer_set_buffer,  3),
    [9]  = CT_MODULE_ENTRY("push",        ct_module_buffer_push,        2),
    [10] = CT_MODULE_ENTRY("append",      ct_module_buffer_append,      2),
    [11] = CT_MODULE_ENTRY("slice",       ct_module_buffer_slice,       3),
    [12] = CT_MODULE_ENTRY("copy",        ct_module_buffer_copy,        1),
    [13] = CT_MODULE_ENTRY("fill",        ct_module_buffer_fill,        2),
    [14] = CT_MODULE_ENTRY("clear",       ct_module_buffer_clear,       1),
    [15] = CT_MODULE_ENTRY("find-byte",   ct_module_buffer_find_byte,   3),
    [16] = CT_MODULE_ENTRY("find-buffer", ct_module_buffer_find_buffer, 3),
    [17] = CT_MODULE_ENTRY("equals",      ct_module_buffer_equals,      2),
};

#endif // CT_MODULE_BUFFER_H