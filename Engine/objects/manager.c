#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "common/error.h"

#include "objects/manager.h"
#include "core/context.h"
#include "objects/object.h"
#include "utils/utils.h"


typedef struct CtObjectBucket {
	uint32_t                id;
	uint64_t                bitmask;
	CtObject*               objects[64];
	struct CtObjectBucket*  next_bucket;
} CtObjectBucket;


struct CtObjectManager {
	CtObjectBucket*     buckets_list;
	uint32_t            bucket_count;
	CtObjectBucket*     empty_buckets_list;
};


CtObjectManager*
ct_objects_init() {

	CtObjectManager* manager = malloc(sizeof(CtObjectManager));
	
	manager->buckets_list = NULL;
	manager->bucket_count = 0;
	
	manager->empty_buckets_list = NULL;

	ct_objects_new_bucket(manager);

	return manager;
}


void
ct_objects_end(CtObjectManager** manager_ptr) {

	CtObjectManager* manager = *manager_ptr;

	CT_LOG("objects", "Starting cleanup.\n");

	CtObjectBucket* current_bucket = manager->buckets_list;

	while (current_bucket != NULL) {
		
		for (uint32_t j = 0; j < sizeof(current_bucket->objects)/sizeof(current_bucket->objects[0]); j++) {
			if (ct_utils_is_bit_set(current_bucket->bitmask, j)) {
				free(current_bucket->objects[j]);
			}
		}

		CtObjectBucket* bucket_to_free = current_bucket;
		current_bucket = current_bucket->next_bucket;

		free(bucket_to_free);
	}
	
	free(manager);
	manager_ptr = NULL;

	CT_LOG("objects", "All objects unallocated.\n");
}


uint32_t
ct_objects_new_bucket(CtObjectManager* manager) {
	
	CtObjectBucket* bucket = malloc(sizeof(CtObjectBucket));

	if (bucket == NULL) {
		CT_ERROR_ENGINE(
			ct_thread_error,
			"Objects",
			"BucketAllocation",
			"Failed to allocate memory for new bucket.", NULL
		);
		return 0;
	}

	bucket->id = manager->bucket_count;
	manager->bucket_count++;

	memset(bucket->objects, 0, sizeof(bucket->objects));

	bucket->next_bucket = manager->buckets_list;
	manager->buckets_list = bucket;
	
	ct_objects_push_empty_bucket(manager, bucket);

	CT_LOG("objects", "New bucket (%u) [%p] allocated. Pushed it to empty buckets stack.\n", bucket->id, bucket);
	return bucket->id;
};


// Mark a bucket as empty and push it to the empty buckets stack
void
ct_objects_push_empty_bucket(CtObjectManager* manager, CtObjectBucket* bucket) {
	
	bucket->next_bucket = manager->empty_buckets_list;
	manager->empty_buckets_list = bucket;

};


CtObjectBucket*
ct_objects_pop_empty_bucket(CtObjectManager* manager) {

	CtObjectBucket* bucket = manager->empty_buckets_list;

	if (bucket == NULL) return NULL;
	
	manager->empty_buckets_list = bucket->next_bucket;

	return bucket;
};


CtObject*
ct_objects_new_object(CtObjectManager* manager, uint32_t size, uint64_t type, CtObjectDeleteFunc del_func) {

	CtObjectBucket* assigned_bucket = NULL;

	assigned_bucket = ct_objects_pop_empty_bucket(manager);
	
	// Have to allocate a new bucket if no bucket was found
	if (!assigned_bucket) {
		ct_objects_new_bucket(manager);
		assigned_bucket = ct_objects_pop_empty_bucket(manager);
	}
	
	uint32_t assigned_obj_slot;

	// Looking for a valid index to assign the Object to in the bucket
	for (uint32_t j = 0; j < sizeof(assigned_bucket->objects)/sizeof(assigned_bucket->objects[0]); j++) {

		if (ct_utils_is_bit_set(assigned_bucket->bitmask, j)) {
			continue;;
		}

		assigned_obj_slot = j;

		ct_utils_set_bit(&assigned_bucket->bitmask, j);

		if (assigned_bucket->bitmask == 0xFFFFFFFFFFFFFFFF) {
			CT_LOG("objects", "Bucket (%u) [%p] is full, so did not push to empty buckets stack.\n", assigned_bucket->id, assigned_bucket);
		} else {
			CT_LOG("objects", "Bucket (%u) [%p] is not full, so pushed to empty buckets stack.\n", assigned_bucket->id, assigned_bucket);
			ct_objects_push_empty_bucket(manager, assigned_bucket);
		}

		break;
	};

	// allocating the object
	CtObject* obj = malloc(size);

	if (obj == NULL) {
		ct_utils_clear_bit(&assigned_bucket->bitmask, assigned_obj_slot);

		CT_ERROR_ENGINE(
			ct_thread_error,
			"Objects",
			"OutOfMemory",
			"Engine failed to allocate memory for new Object (%u.%u). Out of memory.", assigned_bucket->id, assigned_obj_slot
		);
		CT_LOG("objects", "Failed to allocate memory for Object (%u.%u) [%p] of size %u\n", assigned_bucket->id, assigned_obj_slot, obj, size);
		return NULL;
	}
	
	obj->manager = manager;
	obj->bucket_id = assigned_bucket->id;
	obj->bucket_index = assigned_obj_slot;
	obj->bucket = assigned_bucket;
	obj->ref_count = 0;
	obj->type = type;
	obj->size = size;
	obj->delete = del_func;


	CT_LOG("objects", "New Object (%u.%u) [%p] (data:%u bytes) allocated to bucket (%u)\n", obj->bucket_id, obj->bucket_index, obj, size, assigned_bucket->id);

	return obj;
}


void
ct_objects_del_object(CtObjectManager* manager, CtObject* obj) {

	
	CtObjectBucket* bucket = obj->bucket;

	if (bucket->bitmask == 0xFFFFFFFFFFFFFFFF) {
		ct_objects_push_empty_bucket(manager, bucket);
	};

	ct_utils_clear_bit(&bucket->bitmask, obj->bucket_index);

	if (obj->delete) {
		obj->delete(manager, obj);
	}

	CT_LOG("objects", "Object (%u.%u) [%p] unallocated.\n", obj->bucket_id, obj->bucket_index, obj);

	free(obj);
}
