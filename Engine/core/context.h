

#ifndef ENGINE_CONTEXT_H
#define ENGINE_CONTEXT_H

#include <stdint.h>
#include <threads.h>

#include "image/image.h"

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"

#include "objects/manager.h"
#include "objects/object.h"


extern thread_local CtError ct_thread_error;


// Array of atoms and their types. For use in call frames
typedef struct {
	CtAtom         atoms[CT_CONF_FIXED_SLOT_COUNT];
	CtAtomTypeSize types[CT_CONF_FIXED_SLOT_COUNT];
} CtAtomFile;


// a call frame
typedef struct {
	uint32_t            procedure_id;
	uint32_t            return_ip;
	uint8_t             object_field_count;
	uint8_t             args_count;
	uint8_t             return_value_slot;
	CtAtomFile          file;
} CtCallFrame;


// call stack, statically sized
typedef struct {
	CtCallFrame* frames;
	uint32_t     size;
	uint32_t     capacity;
} CtCallStack;


// context specifies the state of execution. 
struct CtContext;
typedef struct CtContext CtContext;


// Create a new context. Requires the image to be ran and the starting procedure.
CtContext*
ct_ctx_new(CtImage* img, CtObjectManager* objects, uint32_t procedure_id);

// Free the context and its resources.
void
ct_ctx_del(CtContext* ctx);

// Setup a callframe, copy the specified arguments from the caller's frame and return value to the specified return slot.
void
ct_ctx_call_procedure(CtContext* ctx, uint32_t procedure_id, uint8_t arg_start_slot, uint8_t return_slot);

// Return from the last called procedure.
void
ct_ctx_return_procedure(CtContext* ctx, CtAtom returned_atom, CtAtomType returned_atom_type);

// Call a module method
void
ct_ctx_modcall(CtContext* ctx, uint32_t module_id, uint32_t method_id, uint8_t arg_start_slot, uint8_t return_slot);

// Read data from the data portion of the image
const uint8_t*
ct_ctx_read_data(CtContext* ctx, uint32_t index);

// Get the object manager pointer of this context
CtObjectManager*
ct_ctx_get_object_manager(CtContext* ctx);

#endif // ENGINE_CONTEXT_H
