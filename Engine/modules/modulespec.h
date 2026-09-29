#ifndef ENGINE_MODULESPEC_H
#define ENGINE_MODULESPEC_H

#include <stdint.h>

#include "common/atom.h"

#include "core/context.h"

#include "utils/utils.h"

typedef struct {
	CtContext*                   context;
	const CtAtom* const          argument_atoms;
	const CtAtomTypeSize* const  argument_types;
} CtModuleMethodArguments;


typedef struct {
	CtAtom         returned_atom;
	CtAtomTypeSize returned_type;
} CtModuleMethodResult;


typedef void (*CtModuleMethod)(CtModuleMethodArguments, CtModuleMethodResult*);

typedef struct {
	char*          name;
	CtModuleMethod method;
	uint32_t       argument_count;
} CtModuleMethodEntry;


#define CT_MODULE_NAME_DEFINE(NAME, STRING) static const char* _ct_module_ ## NAME ## _name = STRING;
#define CT_MODULE_NAME(NAME) (_ct_module_ ## NAME ## _name)
#define CT_MODULE_METHOD_MAP_DEFINE(NAME) CtModuleMethodEntry _ct_module_ ## NAME ## _method_map[]
#define CT_MODULE_METHOD_MAP(NAME) _ct_module_ ## NAME ## _method_map
#define CT_MODULE_ENTRY(NAME, METHOD, ARG_COUNT) (CtModuleMethodEntry) {NAME, METHOD, ARG_COUNT}
#define CT_MODULE_COUNT_METHODS(NAME) sizeof(CT_MODULE_METHOD_MAP(NAME)) / sizeof(CT_MODULE_METHOD_MAP(NAME)[0]) 


// Short hand for getting a primitive. CtModuleMethodArguments must be args, and CtModuleMethodResult must be result. 
#define CT_MODCALL_PRIMIT_ARG(INDEX, TYPE, NAME, ACCESSOR) \
if (args.argument_types[INDEX] != CT_ATOM_PRIMITIVE) { \
	CT_ERROR_ENGINE( \
		ct_thread_error, \
		"Module", \
		"TypeMismatch", \
		"Expected Primitive, got Object.", \
		NULL \
	); \
	return; \
}\
TYPE NAME = (TYPE) (args.argument_atoms[INDEX].ACCESSOR); \

// Short hand for getting an object. CtModuleMethodArguments must be args, and CtModuleMethodResult must be result. 
#define CT_MODCALL_OBJECT_ARG(INDEX, TYPE, NAME) \
if (args.argument_types[INDEX] != CT_ATOM_OBJECT) { \
	CT_ERROR_ENGINE( \
		ct_thread_error, \
		"Module", \
		"TypeMismatch", \
		"Expected Object, got Primtive.", \
		NULL \
	); \
	return; \
}\
TYPE NAME = (TYPE) (args.argument_atoms[INDEX].as_object); \


#define CT_MODCALL_OBJECT_TYPE_CHECK(VAR, TYPEHASH, NAME) \
if (!ct_object_check_type((CtObject*) VAR, TYPEHASH)) { \
	CT_ERROR_ENGINE( \
		ct_thread_error, \
		"Module", \
		"TypeMismatch", \
		"Expected %s object.", \
		NAME, NULL \
	); \
	return; \
}\

#define CT_MODCALL_RESULT(ACCESSOR, VALUE, TYPE) \
result->returned_atom.ACCESSOR = VALUE; \
result->returned_type = TYPE; \

#endif // ENGINE_MODULESPEC_H
