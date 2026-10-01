#ifndef CUTE_OBJECT_H
#define CUTE_OBJECT_H

#include <stdint.h>

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"



struct CtObject;
typedef struct CtObject CtObject;

struct CtObjectBucket;
typedef struct CtObjectBucket CtObjectBucket;

struct CtObjectManager;
typedef struct CtObjectManager CtObjectManager;


struct CtObject {
	CtObjectManager*        mgr;
	CtObjectBucket*         bucket;
	uint32_t                id;
	uint32_t                ref_count;
	uint32_t                size;
	CtAtom*                 atoms;
	CtAtomTypeSize*         types;
}; 


struct CtObjectBucket {
	uint32_t                id;
	uint64_t                bitmask;
	CtObject                objects[64];
	CtObjectBucket*         next_bucket;
};


struct CtObjectManager {
	uint32_t            bucket_count;
	uint32_t            bucket_list_cap;
	CtObjectBucket**    buckets_list;
	CtObjectBucket*     empty_buckets_stack;
};



// Startup the object manager.
void
ct_obj_init_mgr(CtObjectManager* mgr);

// End the Object manager and all its resources.
void
ct_obj_end_mgr(CtObjectManager* mgr);

// Allocate a new object.
CtObject*
ct_obj_create(CtObjectManager* mgr, uint32_t size);

// Delete an object.
void
ct_obj_delete(CtObjectManager* mgr, CtObject* obj);

// Get an atom in the container.
CtTypedAtom
ct_obj_get(CtObjectManager* manager, CtObject* obj, uint32_t index);

// Set an atom in the container.
void
ct_obj_set(CtObjectManager* manager, CtObject* obj, uint32_t index, CtTypedAtom atom);

// Get a byte in the container.
uint8_t
ct_obj_get_byte(CtObjectManager* manager, CtObject* obj, uint32_t index);

// Set a byte in the container.
void
ct_obj_set_byte(CtObjectManager* manager, CtObject* obj, uint32_t index, uint8_t byte);

// Resize an object.
void
ct_obj_resize(CtObjectManager* manager, CtObject* obj, uint32_t new_size);

// Create a shallow copy of an object
CtObject*
ct_obj_copy(CtObjectManager* manager, CtObject* obj);

// Increase the refcount of the object.
static inline void
ct_obj_inc_ref(CtObjectManager* mgr, CtObject* obj) {
	obj->ref_count++;
	CT_LOG("objects", "Object (%u.%u) [%p] referenced. References: %u\n", obj->id, obj->bucket->id, obj, obj->ref_count);
}

// Decrease the ref count of an object. Returns true if the object is deleted.
static inline bool
ct_obj_dec_ref(CtObjectManager* mgr, CtObject* obj) {
	obj->ref_count--;
	CT_LOG("objects", "Object (%u.%u) [%p] dereferenced. References: %u\n", obj->id, obj->bucket->id, obj, obj->ref_count);
	if (obj->ref_count == 0) {
		ct_obj_delete(mgr, obj);
		return true;
	}
	return false;
}

#endif // CUTE_OBJECT_H