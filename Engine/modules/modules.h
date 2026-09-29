
#ifndef ENGINE_MODULES_H
#define ENGINE_MODULES_H

#include "common/error.h"
#include "core/context.h"
#include "modules/modulespec.h"

#include "modules/buffer.h"



/*
Module registration for the Cute Engine.

How to use the dispatch map:
	map[index] -> module_map: gives you the dispatch table for the module at index.
	module_map maybe NULL if the module is not included in the build.
	module_map[index] gives you a CtModuleMethod which can be called. These can never be NULL.
*/


static const CtModuleMethodEntry* ct_modules_dispatch_map[] = {
	[0] = CT_MODULE_METHOD_MAP(buffer),
};

static const uint32_t ct_modules_method_count[] = {
	[0] = CT_MODULE_COUNT_METHODS(buffer),
};

static const uint32_t ct_modules_count = sizeof(ct_modules_dispatch_map) / sizeof(ct_modules_dispatch_map[0]);



static inline int32_t
ct_modules_get_method(uint32_t module_id, uint32_t method_id, CtModuleMethodEntry* entry) {

	if (module_id >= ct_modules_count) {
		CT_ERROR_ENGINE(
			ct_thread_error,
			"Modules",
			"ModuleNotFound",
			"Unknown Module %u called.", 
			module_id
		);
		return 0;
	}

	const CtModuleMethodEntry* module_map = ct_modules_dispatch_map[module_id];

	if (module_map == NULL) {
		CT_ERROR_ENGINE(
			ct_thread_error,
			"Modules",
			"ModuleNotFound",
			"Unknown Module %u called.", 
			module_id
		);
		return 0;
	};

	if (method_id >= ct_modules_method_count[module_id]) {
		CT_ERROR_ENGINE(
			ct_thread_error,
			"Modules",
			"MethodNotFoung",
			"Unknown Method %u called for Module %u.", 
			method_id, module_id
		);
		return 0;
	};

	*entry = module_map[method_id];

	return 1;
};

#endif // ENGINE_MODULES_H
