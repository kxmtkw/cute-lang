#ifndef CUTE_INSTR_H
#define CUTE_INSTR_H


#include <stdint.h>
#include <stdio.h>
#include <string.h>


// Versioning

typedef struct {
	uint32_t major;
	uint32_t minor;
	uint32_t patch;
} CtVersion;

static const CtVersion ct_version = {1, 0, 0};


// Main Cute Instruction Set.
typedef enum {

    CT_INSTR_NULL         = 0x00,
    CT_INSTR_HALT         = 0x01,
    CT_INSTR_OUT          = 0x02,
    
    CT_INSTR_MOV          = 0x20,

	CT_INSTR_LOAD_I16      = 0x21,
    CT_INSTR_LOAD_I32      = 0x22,
    CT_INSTR_LOAD_U32      = 0x23,
    CT_INSTR_LOAD_F32      = 0x24,
	CT_INSTR_LOAD_BYTE     = 0x25,

	CT_INSTR_READ_I64      = 0x26,
	CT_INSTR_READ_U64      = 0x27,
	CT_INSTR_READ_F64      = 0x28,

    CT_INSTR_CAST_I2F     = 0x2A,
    CT_INSTR_CAST_F2I     = 0x2B,
    CT_INSTR_CAST_U2F     = 0x2C,
    CT_INSTR_CAST_F2U     = 0x2D,

    CT_INSTR_ADDI         = 0x30,
    CT_INSTR_SUBI         = 0x31,
    CT_INSTR_MULI         = 0x32,
    CT_INSTR_DIVI         = 0x33,
    CT_INSTR_MODI         = 0x34,
    CT_INSTR_NEGI         = 0x35,
    CT_INSTR_ABSI         = 0x36,

	CT_INSTR_DIVU         = 0x37,
    CT_INSTR_MODU         = 0x38,

	CT_INSTR_INC          = 0x3A,
    CT_INSTR_DEC          = 0x3B,

    CT_INSTR_ADDF         = 0x50,
    CT_INSTR_SUBF         = 0x51,
    CT_INSTR_MULF         = 0x52,
    CT_INSTR_DIVF         = 0x53,
    CT_INSTR_NEGF         = 0x54,
    CT_INSTR_ABSF         = 0x55,    

    CT_INSTR_LOGIC_AND    = 0x60,
    CT_INSTR_LOGIC_OR     = 0x61,
    CT_INSTR_LOGIC_NOT    = 0x62,
    CT_INSTR_LOGIC_XOR    = 0x63,

    CT_INSTR_BIT_AND      = 0x70,
    CT_INSTR_BIT_OR       = 0x71,
    CT_INSTR_BIT_NOT      = 0x73,
    CT_INSTR_BIT_XOR      = 0x74,
    CT_INSTR_BIT_SHL      = 0x75,
    CT_INSTR_BIT_SHR      = 0x76, 
    CT_INSTR_BIT_SHRA     = 0x77, 

    CT_INSTR_CMPI         = 0x80,
    CT_INSTR_CMPU         = 0x81,
    CT_INSTR_CMPF         = 0x82,

    CT_INSTR_EQ           = 0x90,
    CT_INSTR_NOT_EQ       = 0x91,
    CT_INSTR_LESS         = 0x92,
    CT_INSTR_LESS_EQ      = 0x93,
    CT_INSTR_GREATER      = 0x94,
    CT_INSTR_GREATER_EQ   = 0x95,

    CT_INSTR_JMP          = 0xA0,
    CT_INSTR_JMP_EQ       = 0xA1,
    CT_INSTR_JMP_NE       = 0xA2,
    CT_INSTR_JMP_GT       = 0xA3,
    CT_INSTR_JMP_GE       = 0xA4,
    CT_INSTR_JMP_LT       = 0xA5,
    CT_INSTR_JMP_LE       = 0xA6,
	CT_INSTR_JMP_IF       = 0xA7,
	CT_INSTR_JMP_IFNOT    = 0xA8,

    CT_INSTR_CALL         = 0xB0,
    CT_INSTR_RETURN       = 0xB1,
    CT_INSTR_RETURN_VAL   = 0xB2,
    CT_INSTR_MOD_CALL     = 0xBA,

    CT_INSTR_CON_NEW      = 0xC0,
    CT_INSTR_CON_GET      = 0xC1,
    CT_INSTR_CON_SET      = 0xC2,
    CT_INSTR_CON_SIZE     = 0xC3,
    CT_INSTR_CON_COPY     = 0xC4,

} CtInstr;

// All instructions should be able to fit inside this. Allows for 256 different instructions
typedef uint8_t CtInstrSize;


static const uint32_t ct_magic_id = 0x63757465; 

typedef uint8_t CtDataBlobUnit;

typedef struct {
	uint32_t magic_id;
	CtVersion version;
	uint32_t data_blob_size;
	uint32_t procedure_count;
	uint32_t instruction_count;
} CtImageHeader;


typedef struct {
	uint32_t bytecode_index;
	uint32_t arg_count;
} CtImageProcedure;


typedef struct {
	CtImageHeader       header;
	CtDataBlobUnit*     data_blob;
	CtImageProcedure*   procedure_table;
	CtInstrSize*        instruction_pool;
} CtImage;


typedef struct {
	CtImage  image;
	uint32_t procedure_cap;
	uint32_t instruction_cap;
	uint32_t data_blob_cap;
} CtImageBuilder;


// Intialize an empty image builder
void
ct_image_builder_init(CtImageBuilder* builder, uint32_t blob_reserve, uint32_t procedure_reserve, uint32_t instr_reserve);

// Frees the image's resources
void
ct_image_builder_del(CtImageBuilder* builder);

// Create a new procedure entry at the current instruction pool index.
// The return number is the address of the procedure.
uint32_t
ct_image_builder_new_proc(CtImageBuilder* builder, uint32_t id, uint32_t arg_count);

// Get the address of a specific byte offset in the pool.
uint8_t*
ct_image_builder_get_address(CtImageBuilder* builder, uint32_t index);

// Add an instruction to the pool
void
ct_image_builder_add_instr(CtImageBuilder* builder, CtInstrSize instr);

// Add a u8 to the instruction pool
void
ct_image_builder_add_u8(CtImageBuilder* builder, uint8_t i);

// Add a u16 to the instruction pool. Handles endian-ness
void
ct_image_builder_add_u16(CtImageBuilder* builder, uint16_t i);

// Add a u32 to the instruction pool.  Handles endian-ness
void
ct_image_builder_add_u32(CtImageBuilder* builder, uint32_t i);

// Add a f32 to the instruction pool. Handles endian-ness
void
ct_image_builder_add_f32(CtImageBuilder* builder, float f);

// Add data to the data blob, returns the offset.
// Does NOT handle endian-ness for integars, thats the user's responsibility.
uint32_t
ct_image_builder_append_data(CtImageBuilder* builder, uint8_t* data, uint32_t size);


typedef enum {
	CT_IMAGE_STATUS_SUCCESS = 0x0,
	CT_IMAGE_STATUS_FILE_NOT_FOUND = 0x1,
	CT_IMAGE_STATUS_CORRUPTED_IMAGE = 0x2,
	CT_IMAGE_STATUS_VERSION_MISTMATCH = 0x3,
	CT_IMAGE_STATUS_READ_WRITE_FAILURE = 0x4,
} CtImageStatus;


// Write an already initialized image to a file
CtImageStatus
ct_image_dump(CtImage *img, const char *filepath);

// Set an image from a file
CtImageStatus
ct_image_load(CtImage *img, const char *filepath);

// Free the image's resources.
void 
ct_image_free(CtImage *img);


void 
ct_image_print(const CtImage* image);


#if defined(__BYTE_ORDER__) && (__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)
#define CT_HOST_IS_LITTLE_ENDIAN 1
#else
#define CT_HOST_IS_LITTLE_ENDIAN 0
#endif



// Convert big endian to little endian while perserves little endian values.
// Always use this when reading/writing an integer to an image file. 
// This is to ensure that the image file is always in little endian format, regardless of the host architecture.
static inline uint32_t
ct_image_byteswap_u32(uint32_t value) {

	#if CT_HOST_IS_LITTLE_ENDIAN

	return value;
	
	#else

	uint8_t* be = (uint8_t*) &value;
	uint32_t le = (
		((uint32_t) be[3]) << 24 |
		((uint32_t) be[2]) << 16 |
		((uint32_t) be[1]) << 8  |
		((uint32_t) be[0])
	);
	return le;

	#endif // CT_HOST_IS_BIG_ENDIAN

}

// Convert big endian u64 to little endian u64 while perserves little endian values.
static inline uint64_t
ct_image_byteswap_u64(uint64_t value) {

	#if CT_HOST_IS_LITTLE_ENDIAN

	return value;

	#else

	uint8_t* be = (uint8_t*) &value;
	uint64_t le = (
		((uint64_t) be[7]) << 56 |
		((uint64_t) be[6]) << 48 |
		((uint64_t) be[5]) << 40 |
		((uint64_t) be[4]) << 32 |
		((uint64_t) be[3]) << 24 |
		((uint64_t) be[2]) << 16 |
		((uint64_t) be[1]) << 8  |
		((uint64_t) be[0])
	);

	return le;

	#endif // CT_HOST_IS_BIG_ENDIAN

}

// This is to ensure that the image file is always in little endian format, regardless of the host architecture.
static inline uint16_t
ct_image_byteswap_u16(uint16_t value) {

	#if CT_HOST_IS_LITTLE_ENDIAN

	return value;
	
	#else

	uint8_t* be = (uint8_t*) &value;
	uint16_t le = (
		((uint16_t) be[1]) << 8  |
		((uint16_t) be[0])
	);
	return le;

	#endif // CT_HOST_IS_BIG_ENDIAN

}

// Convert big endian f32 to little endian f32 while perserves little endian values.
static inline float
ct_image_byteswap_f32(float value) {
	uint32_t as_int;
	memcpy(&as_int, &value, sizeof(uint32_t));
	as_int = ct_image_byteswap_u32(as_int);
	memcpy(&value, &as_int, sizeof(uint32_t));
	return value;
}

// Convert big endian f64 to little endian f64 while perserves little endian values.
static inline double
ct_image_byteswap_f64(double value) {
	uint64_t as_int;
	memcpy(&as_int, &value, sizeof(uint64_t));
	as_int = ct_image_byteswap_u64(as_int);
	memcpy(&value, &as_int, sizeof(uint64_t));
	return value;
}

#endif // CUTE_INSTR_H