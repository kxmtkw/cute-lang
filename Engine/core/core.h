#ifndef CUTE_CORE_H
#define CUTE_CORE_H

#include <stdint.h>

#include "image/image.h"

#include "common/error.h"
#include "core/context.h"


typedef struct {
	CtImage             image;
	CtError             error;
	uint8_t             exit_code;
} CtEngine;


// Intialize the engine
void
ct_engine_init(CtEngine* engine);

// End the engine and free all resources
void
ct_engine_end(CtEngine* engine);

// Load an image file. For now, only one image can be loaded.
void
ct_engine_load(CtEngine* engine, const char* filepath);

// Run the engine with a custom context
void
ct_engine_run_context(CtEngine* engine, CtContext* ctx);

// Executes a context, the heart of the engine.
void
ct_engine_exec(CtEngine* engine, CtContext* ctx);

// Run an image file from the command line.
void
ct_engine_run(int argc, char** argv);


#endif // CUTE_CORE_H
