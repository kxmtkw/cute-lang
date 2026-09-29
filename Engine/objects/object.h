#ifndef CUTE_OBJECT_H
#define CUTE_OBJECT_H

#include <stdint.h>

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"


struct CtObjectManager;
typedef struct CtObjectManager CtObjectManager;

struct CtObjectBucket;
typedef struct CtObjectBucket CtObjectBucket;

typedef bool (*CtObjectDeleteFunc) (struct CtObjectManager*, struct CtObject*);

struct CtObject {
	CtObjectManager*        manager;
	CtObjectBucket*         bucket;
	uint32_t                bucket_id;
	uint32_t                bucket_index;
	uint32_t                ref_count;
	uint32_t                size;
	uint32_t                type;
	CtObjectDeleteFunc      delete;
}; 


static inline bool
ct_object_check_type(CtObject* obj, uint32_t hash) {
	return obj->type == hash;
}

#endif // CUTE_OBJECT_H