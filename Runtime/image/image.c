#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "CuteInstr.h"


void 
ct_image_builder_init(CtImageBuilder* builder, uint32_t blob_reserve, uint32_t procedure_reserve, uint32_t instr_reserve) {

	if (!builder) return;

	builder->image.header.magic_id = ct_magic_id;
	builder->image.header.version = ct_version;
	builder->image.header.data_blob_size = 0;
	builder->image.header.procedure_count = 0;
	builder->image.header.instruction_count = 0;

	builder->data_blob_cap = blob_reserve > 16 ? blob_reserve: 16;
	builder->procedure_cap = procedure_reserve > 16 ? procedure_reserve: 16;
	builder->instruction_cap = instr_reserve > 16 ? instr_reserve: 16;

	builder->image.data_blob = (CtDataBlobUnit*) malloc(builder->data_blob_cap * sizeof(CtImageProcedure));
	builder->image.procedure_table = (CtImageProcedure*) malloc(builder->procedure_cap * sizeof(CtImageProcedure));
	builder->image.instruction_pool = (CtInstrSize*) malloc(builder->instruction_cap * sizeof(CtInstrSize));
}


void 
ct_image_builder_del(CtImageBuilder* builder) {

	if (!builder) return;

	ct_image_free(&builder->image);

	builder->procedure_cap = 0;
	builder->instruction_cap = 0;
}


static inline void 
_ct_ensure_instr_cap(CtImageBuilder* builder, uint32_t needed_bytes) {
	uint32_t current_count = builder->image.header.instruction_count;
	uint32_t required = current_count + needed_bytes;

	if (required > builder->instruction_cap) {
		uint32_t new_cap = builder->instruction_cap == 0 ? 16 : builder->instruction_cap;
		while (new_cap < required) {
			new_cap *= 2;
		}
		CtInstrSize* new_pool = (CtInstrSize*)realloc(builder->image.instruction_pool, new_cap * sizeof(CtInstrSize));
		if (!new_pool) {
			return;
		}
		builder->image.instruction_pool = new_pool;
		builder->instruction_cap = new_cap;
	}
}

static inline void 
_ct_ensure_proc_cap(CtImageBuilder* builder, uint32_t needed_count) {
	
	if (needed_count > builder->procedure_cap) {
		uint32_t new_cap = builder->procedure_cap == 0 ? 8 : builder->procedure_cap;
		while (new_cap < needed_count) {
			new_cap *= 2;
		}
		CtImageProcedure* new_table = (CtImageProcedure*)realloc(builder->image.procedure_table, new_cap * sizeof(CtImageProcedure));
		if (!new_table) {
			return;
		}
		builder->image.procedure_table = new_table;
		builder->procedure_cap = new_cap;
	}
}


uint32_t 
ct_image_builder_new_proc(CtImageBuilder* builder, uint32_t id, uint32_t arg_count) {

	uint32_t current_proc_count = builder->image.header.procedure_count;
	
	if (id >= current_proc_count) {
		_ct_ensure_proc_cap(builder, id + 1);
	}	
	
	builder->image.procedure_table[id].bytecode_index = builder->image.header.instruction_count;
	builder->image.procedure_table[id].arg_count = arg_count;

	if (id >= builder->image.header.procedure_count) {
		builder->image.header.procedure_count = id + 1;
	}

	return builder->image.header.instruction_count;
}


uint8_t*
ct_image_builder_get_address(CtImageBuilder* builder, uint32_t index) {
	if (!builder || !builder->image.instruction_pool || index >= builder->image.header.instruction_count) {
		return NULL;
	}
	return &builder->image.instruction_pool[index];
}


void 
ct_image_builder_add_instr(CtImageBuilder* builder, CtInstrSize instr) {
	ct_image_builder_add_u8(builder, instr);
}


void 
ct_image_builder_add_u8(CtImageBuilder* builder, uint8_t i) {
	_ct_ensure_instr_cap(builder, sizeof(uint8_t));
	builder->image.instruction_pool[builder->image.header.instruction_count++] = i;
}


void 
ct_image_builder_add_u16(CtImageBuilder* builder, uint16_t i) {
	i = ct_image_byteswap_u16(i);
	_ct_ensure_instr_cap(builder, sizeof(uint16_t));
	memcpy(builder->image.instruction_pool + builder->image.header.instruction_count, &i, sizeof(uint16_t));
	builder->image.header.instruction_count += sizeof(uint16_t);
}


void 
ct_image_builder_add_u32(CtImageBuilder* builder, uint32_t i) {
	i = ct_image_byteswap_u32(i);
	_ct_ensure_instr_cap(builder, sizeof(uint32_t));
	memcpy(builder->image.instruction_pool + builder->image.header.instruction_count, &i, sizeof(uint32_t));
	builder->image.header.instruction_count += sizeof(uint32_t);
}


void 
ct_image_builder_add_f32(CtImageBuilder* builder, float f) {
	f = ct_image_byteswap_f32(f);
	_ct_ensure_instr_cap(builder, sizeof(float));
	memcpy(builder->image.instruction_pool + builder->image.header.instruction_count, &f, sizeof(float));
	builder->image.header.instruction_count += sizeof(float);
}


uint32_t
ct_image_builder_append_data(CtImageBuilder* builder, uint8_t* data, uint32_t size) {

	uint32_t current_size = builder->image.header.data_blob_size;

	if (current_size + size >= builder->data_blob_cap) {
		builder->data_blob_cap = (builder->data_blob_cap * 2) + size;
		builder->image.data_blob = (CtDataBlobUnit*) realloc(
			builder->image.data_blob, 
			builder->data_blob_cap * sizeof(CtImageProcedure)
		);
	}

	memcpy(builder->image.data_blob + current_size, data, size);
	builder->image.header.data_blob_size += size;
	return current_size;
}



CtImageStatus 
ct_image_dump(CtImage *img, const char *filepath) {

	FILE *fp = fopen(filepath, "wb");
	if (!fp) {return CT_IMAGE_STATUS_FILE_NOT_FOUND;}

	img->header.magic_id = ct_magic_id;
	img->header.version = ct_version;

	uint32_t items_written;

	items_written = fwrite(&img->header, sizeof(CtImageHeader), 1, fp);
	if (items_written != 1) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	items_written = fwrite(img->data_blob, sizeof(CtDataBlobUnit), img->header.data_blob_size, fp);
	if (items_written != img->header.data_blob_size) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	items_written = fwrite(img->procedure_table, sizeof(CtImageProcedure), img->header.procedure_count, fp);
	if (items_written != img->header.procedure_count) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	items_written = fwrite(img->instruction_pool, sizeof(CtInstrSize), img->header.instruction_count, fp);
	if (items_written != img->header.instruction_count) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	fclose(fp);
	return CT_IMAGE_STATUS_SUCCESS;
}


CtImageStatus 
ct_image_load(CtImage *img, const char *filepath) {

	FILE *fp = fopen(filepath, "rb");
	if (!fp) {return CT_IMAGE_STATUS_FILE_NOT_FOUND;}

	uint32_t items_read;

	items_read = fread(&img->header, sizeof(CtImageHeader), 1, fp);
	if (items_read != 1) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	if (img->header.magic_id != ct_magic_id) {
		return CT_IMAGE_STATUS_CORRUPTED_IMAGE;
	}

	if (memcmp(&img->header.version, &ct_version, sizeof(ct_version)) != 0) {
		img->header.magic_id = 0;
		return CT_IMAGE_STATUS_VERSION_MISTMATCH;
	}

	img->data_blob = malloc(sizeof(CtDataBlobUnit) * img->header.data_blob_size);
	items_read = fread(img->data_blob, sizeof(CtDataBlobUnit), img->header.data_blob_size, fp);
	if (items_read != img->header.data_blob_size) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	img->procedure_table = malloc(sizeof(CtImageProcedure) * img->header.procedure_count);
	items_read = fread(img->procedure_table, sizeof(CtImageProcedure), img->header.procedure_count, fp);
	if (items_read != img->header.procedure_count) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}

	img->instruction_pool = malloc(sizeof(CtInstrSize) * img->header.instruction_count);
	items_read = fread(img->instruction_pool, sizeof(CtInstrSize), img->header.instruction_count, fp);
	if (items_read != img->header.instruction_count) {return CT_IMAGE_STATUS_READ_WRITE_FAILURE;}
	
	fclose(fp);
	return CT_IMAGE_STATUS_SUCCESS;
};


void 
ct_image_free(CtImage* img)
{
	img->header.instruction_count = 0;
	img->header.procedure_count = 0;


	if (img->procedure_table != NULL) {
		free(img->procedure_table);
		img->procedure_table = NULL;
	}

	if (img->instruction_pool != NULL) {
		free(img->instruction_pool);
		img->instruction_pool = NULL;
	}
};


void ct_image_print(const CtImage* image) {
    if (!image) {
        printf("CtImage: NULL\n");
        return;
    }

    printf("================ [ CtImage ] ================\n");
    printf("Header:\n");
    printf("  Magic ID:          0x%08X\n", image->header.magic_id);
    printf("  Version:           %d.%d.%d\n", image->header.version.major, image->header.version.minor, image->header.version.patch);
    printf("  Data Blob Size:    0x%08X (%u bytes)\n", image->header.data_blob_size, image->header.data_blob_size);
    printf("  Procedure Count:   0x%X (%u)\n", image->header.procedure_count, image->header.procedure_count);
    printf("  Instruction Count: 0x%X (%u)\n", image->header.instruction_count, image->header.instruction_count);
    printf("---------------------------------------------\n");

    printf("Data Blob:\n");
    if (image->data_blob && image->header.data_blob_size > 0) {
        for (uint32_t i = 0; i < image->header.data_blob_size; ++i) {
            printf("  Blob [%08X]: 0x%02X\n", i, image->data_blob[i]);
        }
    } else {
        printf("  (empty or null data blob)\n");
    }

    printf("---------------------------------------------\n");
    printf("Procedure Table:\n");
    if (image->procedure_table && image->header.procedure_count > 0) {
        for (uint32_t i = 0; i < image->header.procedure_count; ++i) {
            printf("  Proc [%04X]: Bytecode Index = 0x%08X, Arg Count = 0x%X (%u)\n",
                   i,
                   image->procedure_table[i].bytecode_index,
                   image->procedure_table[i].arg_count,
                   image->procedure_table[i].arg_count);
        }
    } else {
        printf("  (empty or null procedure table)\n");
    }

    printf("---------------------------------------------\n");
    printf("Instruction Pool:\n");
    if (image->instruction_pool && image->header.instruction_count > 0) {
        for (uint32_t i = 0; i < image->header.instruction_count; ++i) {
            printf("  Instr [%08X]: 0x%02X\n",
                   i,
                   image->instruction_pool[i]);
        }
    } else {
        printf("  (empty or null instruction pool)\n");
    }
    printf("=============================================\n");
}