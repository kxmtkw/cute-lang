
#ifndef CUTE_CONTAINER_H
#define CUTE_CONTAINER_H

#include <stdint.h>

#include "common/atom.h"
#include "common/error.h"

#include "objects/manager.h"


typedef struct {
	CtObject            __object__;
	uint32_t            sub_objects;
	uint32_t            size;
	CtAtom*             atoms;
	CtAtomTypeSize*     types;
} CtContainer;


CtContainer*
ct_container_new(CtObjectManager* manager, uint32_t size);


bool
ct_container_del(CtObjectManager* manager, CtObject* obj);


static inline uint32_t
ct_container_size(CtObjectManager* manager, CtContainer* obj) {
	return obj->size;
};


// Get an atom in the container. Will return ctConManagerCode_OutOfBounds if index is out of bounds
CtTypedAtom
ct_container_get(CtObjectManager* manager, CtContainer* obj, uint32_t index);

// Set an atom in the container. Will return ctConManagerCode_OutOfBounds if index is out of bounds.
void
ct_container_set(CtObjectManager* manager, CtContainer* obj, uint32_t index, CtTypedAtom atom);

// Create a shallow copy of a container
CtContainer*
ct_container_copy(CtObjectManager* manager, CtContainer* obj);

#endif // CONTAINERS_CONTAINER_H
