#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "common/atom.h"
#include "common/config.h"
#include "common/error.h"

#include "core/context.h"
#include "objects/manager.h"

#include "container.h"

#include "utils/utils.h"



CtContainer*
ct_container_new(CtObjectManager* manager, uint32_t size) {

	uint32_t req_size = sizeof(CtContainer) + sizeof(CtAtom) * size + sizeof(CtAtomTypeSize) * size;

	CtObject* obj = ct_objects_new_object(manager, req_size, 0 /*placeholder*/, ct_container_del);
	CtContainer* container = (CtContainer*) obj;

	if (obj == NULL) {
		return NULL;
	}
	
	uint8_t* data = (uint8_t*) obj;
	container->atoms = (CtAtom*) (data + sizeof(CtContainer));
	container->types = (CtAtomTypeSize*) (data + sizeof(CtContainer) + sizeof(CtAtom) * size);
	container->size = size;
	container->sub_objects = 0;

	CT_LOG("containers", "New container (%u.%u) [%p] (size:%u atoms) allocated.\n", obj->bucket_id, obj->bucket_index, obj, size);

	return container;
};


bool
ct_container_del(CtObjectManager* manager, CtObject* obj) {

	CtContainer* container = (CtContainer*) obj;

	uint32_t j = 0;
	
	for (uint32_t i = 0; i < obj->size && j < container->sub_objects; i++) {
		if (container->types[i] == CT_ATOM_OBJECT) {
			ct_objects_dec_ref(manager, container->atoms[i].as_object);
			j++;
		}
	}

	CT_LOG("containers", "Deleting container (%u.%u) [%p]\n", obj->bucket_id, obj->bucket_index, obj);
};


// Get an atom in the container. Will return ctConManagerCode_OutOfBounds if index is out of bounds
CtTypedAtom
ct_container_get(CtObjectManager* manager, CtContainer* obj, uint32_t index) {

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
};

// Set an atom in the container. Will return ctConManagerCode_OutOfBounds if index is out of bounds.
void
ct_container_set(CtObjectManager* manager, CtContainer* obj, uint32_t index, CtTypedAtom atom) {

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
		ct_objects_dec_ref(manager, obj->atoms[index].as_object);
		if (obj->sub_objects > 0) obj->sub_objects--;
	}

	obj->atoms[index] = atom.atom;
	obj->types[index] = atom.type;

	if (obj->types[index] == CT_ATOM_OBJECT) {
		ct_objects_inc_ref(manager, obj->atoms[index].as_object);
		obj->sub_objects++; 
	}
}

// Create a shallow copy of a container
CtContainer*
ct_container_copy(CtObjectManager* manager, CtContainer* obj) {
	
	CtContainer* copy = ct_container_new(manager, obj->__object__.size);

	if (copy == NULL) {
		return NULL;
	}

	memcpy(copy->atoms, obj->atoms, obj->size * sizeof(CtAtom));
	memcpy(copy->types, obj->types, obj->size * sizeof(CtAtomTypeSize));

	copy->sub_objects = obj->sub_objects;

	uint32_t j = 0;

	for (uint32_t i = 0; i < obj->size && j < obj->sub_objects; i++) {
		if (obj->types[i] == CT_ATOM_OBJECT) {
			ct_objects_inc_ref(manager, obj->atoms[i].as_object);
			j++;
		}
	}
	
	CT_LOG("containers", "Copied container (%u.%u) [%p] from container (%u.%u) [%p]\n", copy->__object__.bucket_id, copy->__object__.bucket_index, copy, obj->__object__.bucket_id, obj->__object__.bucket_index, obj);

	return copy;
}