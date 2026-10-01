#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"

#include "core/context.h"
#include "objects/object.h"
#include "utils/utils.h"


// Push a bucket to the empty stack. The bucket must be empty
static inline void
ct_obj_mgr_push_empty_bucket(CtObjectManager* mgr, CtObjectBucket* bucket) {
	bucket->next_bucket = NULL;
	bucket->next_bucket = mgr->empty_buckets_stack;
	mgr->empty_buckets_stack = bucket;
}


// Pop a bucket from the empty bucket stack.
static inline CtObjectBucket*
ct_obj_mgr_pop_empty_bucket(CtObjectManager* mgr) {
	CtObjectBucket* bucket = mgr->empty_buckets_stack;
	if (bucket == NULL) return NULL;
	mgr->empty_buckets_stack = mgr->empty_buckets_stack->next_bucket;
	return bucket;
}


// Create a new bucket
static inline CtObjectBucket*
ct_obj_mgr_new_bucket(CtObjectManager* mgr) {

	CtObjectBucket* bucket = malloc(sizeof(CtObjectBucket));

	if (mgr->bucket_count >= mgr->bucket_list_cap) {
		mgr->buckets_list = (CtObjectBucket**) realloc(mgr->buckets_list, mgr->bucket_list_cap * 2);
		mgr->bucket_list_cap *= 2;
	}

	bucket->id = mgr->bucket_count;
	bucket->bitmask = 0;
	memset(bucket->objects, 0, sizeof(bucket->objects));

	mgr->buckets_list[mgr->bucket_count++] = bucket;

	return bucket;
}

void
ct_obj_init_mgr(CtObjectManager* mgr) {
	mgr->buckets_list = malloc(sizeof(CtObjectBucket*) * 8);
	mgr->empty_buckets_stack = NULL;
}

// End the Object manager and all its resources.
void
ct_obj_end_mgr(CtObjectManager* mgr) {
	// todoo
}

// Allocate a new object.
CtObject*
ct_obj_create(CtObjectManager* mgr, uint32_t size) {

	CtObjectBucket* assigned_bucket = NULL;

	assigned_bucket = ct_obj_mgr_pop_empty_bucket(mgr);

	if (assigned_bucket == NULL) {
		assigned_bucket = ct_obj_mgr_new_bucket(mgr);
	}

	uint32_t assigned_obj_slot = 0;

	// Looking for a valid index to assign the Object to in the bucket
	for (uint32_t j = 0; j < sizeof(assigned_bucket->objects)/sizeof(assigned_bucket->objects[0]); j++) {

		if (ct_utils_is_bit_set(assigned_bucket->bitmask, j)) {
			continue;
		}

		assigned_obj_slot = j;

		ct_utils_set_bit(&assigned_bucket->bitmask, j);

		if (assigned_bucket->bitmask == 0xFFFFFFFFFFFFFFFF) {
			CT_LOG("objects", "Bucket (%u) [%p] is full, so did not push to empty buckets stack.\n", assigned_bucket->id, assigned_bucket);
		} else {
			CT_LOG("objects", "Bucket (%u) [%p] is not full, so pushed to empty buckets stack.\n", assigned_bucket->id, assigned_bucket);
			ct_obj_mgr_push_empty_bucket(mgr, assigned_bucket);
		}

		break;
	};

	CtAtom* atoms = malloc(sizeof(CtAtom) * size);
	CtAtomTypeSize* types = malloc(sizeof(CtAtomTypeSize) * size);

	CtObject* obj = &assigned_bucket->objects[assigned_obj_slot];

	*obj = (CtObject) {
		.mgr = mgr,
		.bucket = assigned_bucket,
		.id = assigned_obj_slot,
		.ref_count = 0,
		.size = size,
		.atoms = atoms,
		.types = types
	};

	return obj;
}


void
ct_obj_delete(CtObjectManager* mgr, CtObject* obj) {

	CtObjectBucket* bucket = obj->bucket;

	// the reason we check for whether the bucket is full or not is that if it was not full, it would already be in the empty stack
	if (bucket->bitmask == ~(0ULL)) {
		ct_obj_mgr_push_empty_bucket(mgr, bucket);
	};

	ct_utils_clear_bit(&bucket->bitmask, obj->id);

	CT_LOG("objects", "Object (%u.%u) [%p] unallocated.\n", obj->bucket_id, obj->bucket_index, obj);

	free(obj);
}

// Get an atom in the container.
CtTypedAtom
ct_obj_get(CtObjectManager* manager, CtObject* obj, uint32_t index) {

	if (index >= obj->size) {
		CT_ERROR_ENGINE(
			ct_thread_error,
			"Container",
			"Access",
			"Can not access container slot #%u (>= %u)", index, obj->size
		);
		return (CtTypedAtom){CT_ATOM_PRIMITIVE, (CtAtom){0}};
	}

	return (CtTypedAtom){obj->types[index], obj->atoms[index]};
}

// Set an atom in the container.
void
ct_obj_set(CtObjectManager* manager, CtObject* obj, uint32_t index, CtTypedAtom atom) {

	if (index >= obj->size) {
		CT_ERROR_ENGINE(
			ct_thread_error,
			"Container",
			"Access",
			"Can not access container slot #%u (>= %u)", index, obj->size
		);
		return;
	}

	if (obj->types[index] == CT_ATOM_OBJECT) {
		ct_obj_inc_ref(manager, obj->atoms[index].as_object);
	}

	obj->atoms[index] = atom.atom;
	obj->types[index] = atom.type;

	if (obj->types[index] == CT_ATOM_OBJECT) {
		ct_obj_dec_ref(manager, obj->atoms[index].as_object);
	}
}

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
