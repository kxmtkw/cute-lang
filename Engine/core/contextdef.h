#ifndef ENGINE_CONTEXT_PRIV_H
#define ENGINE_CONTEXT_PRIV_H

// Private Context Header File
// Exists so context's definition can be hidden from the rest of the code
// Should not be included by any file outside of engine/

#include <stdbool.h>
#include <stdint.h>

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"

#include "objects/manager.h"


#include "core/context.h"


// context specifies the state of execution. 
struct CtContext {
	const CtImage*      image;
	CtObjectManager*    objects;
	uint64_t            ip;
	CtCallStack         callstack;
	CtCallFrame*        current_frame;
	double              cmp_diff;
	bool                running;
	uint8_t             exit_code;
};

typedef struct CtContext CtContext;

static inline bool
ct_ctx_is_running(CtContext* ctx) {
	if (ct_thread_error.raised) {
		ctx->running = false;
		ctx->exit_code = 1;
		return false;
	};
	return true;
}

// Store an atom at a specified slot in the CURRENT call frame.
static inline void
ct_ctx_store_atom(CtContext* ctx, uint8_t slot, CtAtom atom, CtAtomType type) {

	if (ctx->current_frame->file.types[slot] == CT_ATOM_OBJECT) {
		ct_objects_dec_ref(ctx->objects, ctx->current_frame->file.atoms[slot].as_object);
		ctx->current_frame->object_field_count--;
	};

	ctx->current_frame->file.atoms[slot] = atom;
	ctx->current_frame->file.types[slot] = type;

	if (type == CT_ATOM_OBJECT) {
		ct_objects_inc_ref(ctx->objects, atom.as_object);
		ctx->current_frame->object_field_count++;
	};
};

// Load an atom from a specified index from the CURRENT call frame.
static inline void
ct_ctx_load_atom(CtContext* ctx, uint8_t slot, CtAtom* atom, CtAtomType* type) {
	*atom = ctx->current_frame->file.atoms[slot];
	*type = ctx->current_frame->file.types[slot];
};

// Move an atom from one slot to another.
static inline void
ct_ctx_move_atom(CtContext* ctx, uint8_t src_slot, uint8_t dest_slot) {

	if (ctx->current_frame->file.types[dest_slot] == CT_ATOM_OBJECT) {
		ct_objects_dec_ref(ctx->objects, ctx->current_frame->file.atoms[dest_slot].as_object);
		ctx->current_frame->object_field_count--;
	};

	ctx->current_frame->file.atoms[dest_slot] = ctx->current_frame->file.atoms[src_slot];
	ctx->current_frame->file.types[dest_slot] = ctx->current_frame->file.types[src_slot];

	if (ctx->current_frame->file.types[src_slot] == CT_ATOM_OBJECT) {
		ct_objects_inc_ref(ctx->objects, ctx->current_frame->file.atoms[src_slot].as_object);
		ctx->current_frame->object_field_count++;
	};
};


#endif // ENGINE_CONTEXT_PRIV_H