#include <stdint.h>
#include <stdlib.h>
#include <time.h>


#include "common/atom.h"
#include "common/config.h"
#include "common/instr.h"
#include "common/error.h"

#include "objects/manager.h"
#include "utils/utils.h"

#include "core/core.h"
#include "core/context.h"
#include "core/contextdef.h"


void
ct_engine_init(CtEngine* engine) {
	CT_LOG("engine", "vroom vroom\n");
	engine->exit_code = 0;
}


void
ct_engine_end(CtEngine* engine) {

	if (engine->image.header.magic_id == ct_magic_id) {
		CT_LOG("engine", "Freeing image resources.\n");
		ct_image_free(&engine->image);
	}

	CT_LOG("engine", "Ending engine.\n");
	exit(engine->exit_code);
}


void
ct_engine_load(CtEngine* engine, const char* filepath) {
	
	CT_LOG("engine", "Loading image file: %s\n", filepath);

	CtImageStatus code = ct_image_load(&engine->image, filepath);

	switch (code) {

		case CT_IMAGE_STATUS_SUCCESS:
			CT_LOG("engine", "Image loaded successfully.\n");
			break;

			case CT_IMAGE_STATUS_FILE_NOT_FOUND:
			CT_ERROR_ENGINE(
				engine->error, 
				"Engine", 
				"ImageNotFound", 
				"Cannot find image file: %s", filepath
			);
			break;

		case CT_IMAGE_STATUS_READ_WRITE_FAILURE:
			CT_ERROR_ENGINE(
				engine->error, 
				"Engine", 
				"ImageReadWriteFailure", 
				"Failed to read image file: %s", filepath
			);
			break;

		case CT_IMAGE_STATUS_CORRUPTED_IMAGE:
			CT_ERROR_ENGINE(
				engine->error, 
				"Engine", 
				"CorruptedImage", 
				"Invalid image file: %s", filepath
			);
			break;

		case CT_IMAGE_STATUS_VERSION_MISTMATCH:
			CT_ERROR_ENGINE(
				engine->error, 
				"Engine", 
				"VersionMismatch", 
				"Version mismatch.", NULL
			);
			break;

		default:
			CT_ERROR_ENGINE(
				engine->error, 
				"Engine", 
				"UnknownImageError", 
				"Unknown failure while reading image file: %s", filepath
			);
			break;
	}

	if (code != CT_IMAGE_STATUS_SUCCESS) {
		ct_error_print(&engine->error);
		engine->exit_code = 1;
		ct_engine_end(engine);
		exit(1);
	}
}


void
ct_engine_run_context(CtEngine* engine, CtContext* ctx) {

	ct_engine_exec(engine, ctx);
	
	if (ct_thread_error.raised) {
		ct_error_print(&ct_thread_error);
	}

	engine->exit_code = ctx->exit_code;
}

void
ct_engine_run(int argc, char** argv) {

	if (argc <= 1) {
		printf("usage: cute <image>\n");
		exit(2);
	}

	CtEngine engine;
	ct_engine_init(&engine);
	ct_engine_load(&engine, argv[1]);

	
	ct_engine_run_context(
		&engine,
		ct_ctx_new(&engine.image, ct_objects_init(), 0)
	);

	ct_engine_end(&engine);

}
