#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"

#include "objects/manager.h"
#include "modules/modules.h"
#include "modules/modulespec.h"
#include "utils/utils.h"

#include "context.h"
#include "contextdef.h"


thread_local CtError ct_thread_error;

// Call Stack helpers

static inline void
ct_ctx_init_call_stack(CtCallStack* s) {
    s->size     = 0;
    s->capacity = CT_CONF_CALLSTACK_SIZE;
	s->frames = malloc(sizeof(CtCallFrame) * s->capacity);
}

static inline void 
ct_ctx_del_call_stack(CtCallStack* s) {
    s->size    = 0;
    s->capacity = 0;
	if (s->frames) free(s->frames);
}

static inline CtCallFrame*
ct_ctx_get_new_frame(CtCallStack* s) {	
	return &s->frames[s->size++];
}

static inline CtCallFrame* 
ct_ctx_pop_frame(CtCallStack* s) {
    if (s->size > 0) {
		return &s->frames[--s->size];
	};	
	return NULL;
}

static inline CtCallFrame* 
ct_ctx_get_top_frame(CtCallStack* s) {
    if (s->size > 0) {
		return &s->frames[s->size-1];
	};	
	return NULL;
}


// Context methods

CtContext*
ct_ctx_new(CtImage* img, CtObjectManager* objects, uint32_t procedure_id) {
	CtContext* ctx = (CtContext*) malloc(sizeof(CtContext));
	ctx->image = img;
	ctx->objects = objects;
	ctx->running = true;
	ctx->current_frame = NULL;
	ct_ctx_init_call_stack(&ctx->callstack);
	ct_ctx_call_procedure(ctx, procedure_id, 0, 0);
	return ctx;
}


void
ct_ctx_del(CtContext* ctx) {
	ct_ctx_del_call_stack(&ctx->callstack);
}


void
ct_ctx_call_procedure(CtContext* ctx, uint32_t procedure_id, uint8_t arg_start_slot, uint8_t return_slot) {

	if (ctx->callstack.size >= CT_CONF_CALLSTACK_SIZE) {
		
		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"RecursionDepth", 
			"Recursion depth reached. Too many calls. (%u)", CT_CONF_CALLSTACK_SIZE
		);

		return;
	};

	if (procedure_id >= ctx->image->header.procedure_count) {

		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"InvalidProcedure", 
			"Procedure %u does not exist.", procedure_id
		);

		return;
	}

	CtImageProcedure proc = ctx->image->procedure_table[procedure_id];
	uint32_t arg_count = procedure_id == 0 ? 0 : proc.arg_count;

	if (arg_count >= CT_CONF_FIXED_SLOT_COUNT) {
		
		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"TooManyArguments", 
			"Too many arguments requested by procedure(%u): '%u' (>=%u)", procedure_id, arg_count, CT_CONF_FIXED_SLOT_COUNT
		);

		return;
	};

	CtCallFrame* frame = ct_ctx_get_new_frame(&ctx->callstack);

	frame->procedure_id = procedure_id;
	frame->object_field_count = 0;
	frame->return_ip = ctx->ip;
	frame->return_value_slot = return_slot;
	frame->args_count = arg_count;
	
	memset(frame->file.types, 0, CT_CONF_FIXED_SLOT_COUNT);

	for (size_t i = 0; i < arg_count; i++) {
		frame->file.atoms[i] = ctx->current_frame->file.atoms[arg_start_slot + i];
		frame->file.types[i] = ctx->current_frame->file.types[arg_start_slot + i];

		if (frame->file.types[i] == CT_ATOM_OBJECT) {
			ct_objects_inc_ref(ctx->objects, frame->file.atoms[i].as_object);
			frame->object_field_count++;
		}
	};
	
	ctx->current_frame = ct_ctx_get_top_frame(&ctx->callstack);
	ctx->ip = proc.bytecode_index;
	
	CT_LOG(
		"context", 
		"Called procedure(%u) with %u arguments passed from previous frame's slot %d. Jumped to address %u.\n", 
		procedure_id, arg_count, arg_start_slot, proc.bytecode_index
	);
}


void
ct_ctx_return_procedure(CtContext* ctx, CtAtom returned_atom, CtAtomType returned_atom_type) {

	CtCallFrame* frame = ct_ctx_pop_frame(&ctx->callstack);
	ctx->current_frame = ct_ctx_get_top_frame(&ctx->callstack);

	if (ctx->current_frame == NULL) {
		ctx->running = false;
		ctx->exit_code = returned_atom.as_uint;
		return;
	}
	
	ctx->ip = frame->return_ip;
	ct_ctx_store_atom(ctx, frame->return_value_slot, returned_atom, returned_atom_type);

	for (size_t i = 0; i < CT_CONF_FIXED_SLOT_COUNT && frame->object_field_count; i++) {
		if (frame->file.types[i] == CT_ATOM_OBJECT) {
			ct_objects_dec_ref(ctx->objects, frame->file.atoms[i].as_object);
			frame->object_field_count--;
		}
	};

	CT_LOG("context", "Returned from procedure(%u) with return value: 0x%lx\n", frame->procedure_id, returned_atom.raw);
}



void
ct_ctx_modcall(CtContext* ctx, uint32_t module_id, uint32_t method_id, uint8_t arg_start_slot, uint8_t return_slot) {

	CtModuleMethodEntry entry;

	uint32_t code = ct_modules_get_method(module_id, method_id, &entry);

	if (!code) {
		return;
	};

	CT_LOG("context", "Calling module method: %u.%u with %u arguments starting from slot %u. Returning to slot %u.\n", module_id, method_id, entry.argument_count, arg_start_slot, return_slot);

	if (arg_start_slot + entry.argument_count > 255) {
		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"FaultyAlignment", 
			"Module method: %u.%u expected %u arguments. Cannot use arguments starting from slot %u.", module_id, method_id, entry.argument_count, arg_start_slot
		);
		return;
	}

	CtModuleMethodArguments args = {
		.context = ctx,
		.argument_atoms = &ctx->current_frame->file.atoms[arg_start_slot],
		.argument_types = &ctx->current_frame->file.types[arg_start_slot],
	};

	CtModuleMethodResult result = {0};

	entry.method(args, &result);

	if (!ct_ctx_is_running(ctx)) {
		return;
	};

	if (ctx->current_frame->file.types[return_slot] == CT_ATOM_OBJECT) {
		ct_objects_dec_ref(ctx->objects, ctx->current_frame->file.atoms[return_slot].as_object);	
	} 
	ctx->current_frame->file.atoms[return_slot] = result.returned_atom;
	ctx->current_frame->file.types[return_slot] = result.returned_type;

	if (result.returned_type == CT_ATOM_OBJECT) {
		ct_objects_inc_ref(ctx->objects, result.returned_atom.as_object);
	}
};


const uint8_t*
ct_ctx_read_data(CtContext* ctx, uint32_t index) {

	if (index >= ctx->image->header.data_blob_size) {
		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"InvalidAccess", 
			"Cannot access data.", NULL
		);
		return NULL;
	}

	return (ctx->image->data_blob + index);
};


CtObjectManager*
ct_ctx_get_object_manager(CtContext* ctx) {
	return ctx->objects;
}