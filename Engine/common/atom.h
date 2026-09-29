#ifndef CUTE_ATOM_H
#define CUTE_ATOM_H

#include <stdbool.h>
#include <stdint.h>


typedef enum {
	CT_ATOM_PRIMITIVE = 0x0,
	CT_ATOM_OBJECT    = 0x1
} CtAtomType;


typedef uint8_t CtAtomTypeSize;

struct CtObject;
typedef struct CtObject CtObject;

typedef union {
	uint64_t             raw;
	int64_t              as_int;
	uint64_t             as_uint;
	double               as_float;
	uint64_t             as_bool;
	struct CtObject*     as_object;
} CtAtom;


typedef struct {
	CtAtomTypeSize type;
	CtAtom         atom;
} CtTypedAtom;


#endif // CUTE_ATOM_H