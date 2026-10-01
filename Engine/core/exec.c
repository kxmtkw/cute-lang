#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "common/atom.h"
#include "common/instr.h"
#include "common/config.h"
#include "common/error.h"


#include "core/core.h"
#include "core/context.h"

#include "objects/object.h"

#include "utils/utils.h"



#define CT_INSTR_BINARYOP(TYPE, FIELD, OP) \
r1 = instrs[ctx->ip++]; \
r2 = instrs[ctx->ip++]; \
r3 = instrs[ctx->ip++]; \
ct_ctx_load_atom(ctx, r2, &a1, &t1); \
ct_ctx_load_atom(ctx, r3, &a2, &t2); \
ct_ctx_store_atom(ctx, r1, (CtAtom){.FIELD = a1.FIELD OP a2.FIELD}, TYPE);


#define CT_INSTR_UNARYOP(TYPE, FIELD, OP) \
r1 = instrs[ctx->ip++]; \
r2 = instrs[ctx->ip++]; \
ct_ctx_load_atom(ctx, r2, &a1, &t1); \
ct_ctx_store_atom(ctx, r1, (CtAtom){.FIELD = OP (a1.FIELD)}, TYPE);


#define CT_INSTR_CMP(TYPE, FIELD) \
r1 = instrs[ctx->ip++]; \
r2 = instrs[ctx->ip++]; \
ct_ctx_load_atom(ctx, r1, &a1, &t1); \
ct_ctx_load_atom(ctx, r2, &a2, &t2); \
ctx->cmp_diff = (double)a1.FIELD - (double)a2.FIELD; 


#define CT_INSTR_CMP_RESOLVER(OP) \
r1 = instrs[ctx->ip++]; \
ct_ctx_store_atom(ctx, r1, (CtAtom){.as_bool = ctx->cmp_diff OP 0 ? 1 : 0}, CT_ATOM_PRIMITIVE); \


#define CT_INSTR_JMP() \
_ct_load_bytes(instrs, &ctx->ip, 4, &i32); \
ctx->ip += i32; \
if (ctx->ip >= engine->image.header.instruction_count) { \
	CT_ERROR_ENGINE( \
		ct_thread_error, \
		"Engine", \
		"IllegalJump", \
		"Out of range ip: 0x%08lX", ctx->ip \
	); \
	return; \
};


#define CT_CHECK_IF_OBJECT(TYPE) \
if (TYPE != CT_ATOM_OBJECT) { \
	CT_ERROR_ENGINE( \
		ct_thread_error, \
		"Engine", \
		"TypeError", \
		"Expected Container, Got Primitive", NULL \
	); \
	return; \
}; \


static inline void
_ct_load_bytes(CtInstrSize* instrs, uint64_t* ip, uint32_t n, void* dest) {
	memcpy(dest, &instrs[*ip], n);
	*ip += n;
}


static inline void
_ct_inc_atom(CtContext* ctx, uint8_t slot) {	
	if (ctx->current_frame->file.types[slot] == CT_ATOM_OBJECT) {
		ct_obj_dec_ref(&ctx->objects, ctx->current_frame->file.atoms[slot].as_object);
		ctx->current_frame->object_field_count--;
		ctx->current_frame->file.types[slot] = CT_ATOM_PRIMITIVE;
	}
	ctx->current_frame->file.atoms[slot].as_uint++;
};


static inline void
_ct_dec_atom(CtContext* ctx, uint8_t slot) {	
	if (ctx->current_frame->file.types[slot] == CT_ATOM_OBJECT) {
		ct_obj_dec_ref(&ctx->objects, ctx->current_frame->file.atoms[slot].as_object);
		ctx->current_frame->object_field_count--;
		ctx->current_frame->file.types[slot] = CT_ATOM_PRIMITIVE;
	};
	ctx->current_frame->file.atoms[slot].as_uint--;
};


static inline void 
_ct_out(uint8_t fmt, CtAtom atom) {

	switch (fmt) {
		
		case 0:
			printf("[ binary ");
			for (int i = 63; i >= 0; i--) {
				printf("%d", (int)((atom.raw >> i) & 1));
				if (i % 8 == 0 && i != 0) printf(" ");
			}
			printf(" ]\n");
			break;
		case 1:
			printf("[ hexadecimal 0x%016lX ]\n", (uint64_t)atom.raw); break;
		case 2:
			printf("[ int %ld ]\n", atom.as_int); break;
		case 3:
			printf("[ uint %lu ]\n", atom.as_uint); break;
		case 4:
			printf("[ float %f ]\n", atom.as_float); break;
		case 5:
			printf("[ bool %s ]\n", atom.as_bool ? "true" : "false"); break;
		case 6:
			printf("[ char %c ]\n", (char) atom.as_uint); break;
		case 7:
			printf("[ object %p ]\n", atom.as_object); break;
		default:
			printf("[ hexadecimal 0x%016lX (unk-format %u) ]\n", (uint64_t)atom.raw, fmt);
	}
}

#ifndef CT_CONF_DEBUG

#define NEXT() if (ct_ctx_is_running(ctx)) {goto *dispatch_table[instrs[ctx->ip++]];} else { return; };

#else 

#define NEXT() if (ct_ctx_is_running(ctx)) { \
	CT_LOG("trace", "ip: 0x%08lX | instr: 0x%02X | ctx: %p\n", ctx->ip, instrs[ctx->ip], ctx); goto *dispatch_table[instrs[ctx->ip++]]; \
} else { return; }

#endif // CUTE_CONF_DEBUG

void
ct_engine_exec(CtEngine* engine, CtContext* ctx) {

	static void* dispatch_table[256] = {
		[CT_INSTR_NULL]       = &&HANDLER_NULL,
		[CT_INSTR_HALT]       = &&HANDLER_HALT,
		[CT_INSTR_OUT]        = &&HANDLER_OUT,

		[CT_INSTR_MOV]        = &&HANDLER_MOV,
		[CT_INSTR_LOAD_I16]   = &&HANDLER_LOAD_I16,
		[CT_INSTR_LOAD_I32]   = &&HANDLER_LOAD_I32,
		[CT_INSTR_LOAD_U32]   = &&HANDLER_LOAD_U32,
		[CT_INSTR_LOAD_F32]   = &&HANDLER_LOAD_F32,
		[CT_INSTR_LOAD_BYTE]  = &&HANDLER_LOAD_BYTE,

		[CT_INSTR_READ_I64]   = &&HANDLER_READ_I64,
		[CT_INSTR_READ_U64]   = &&HANDLER_READ_U64,
		[CT_INSTR_READ_F64]   = &&HANDLER_READ_F64,

		[CT_INSTR_CAST_I2F]    = &&HANDLER_CAST_I2F,
		[CT_INSTR_CAST_F2I]    = &&HANDLER_CAST_F2I,
		[CT_INSTR_CAST_U2F]    = &&HANDLER_CAST_U2F,
		[CT_INSTR_CAST_F2U]    = &&HANDLER_CAST_F2U,

		[CT_INSTR_ADDI]       = &&HANDLER_ADDI,
		[CT_INSTR_SUBI]       = &&HANDLER_SUBI,
		[CT_INSTR_MULI]       = &&HANDLER_MULI,
		[CT_INSTR_DIVI]       = &&HANDLER_DIVI,
		[CT_INSTR_MODI]       = &&HANDLER_MODI,
		[CT_INSTR_NEGI]       = &&HANDLER_NEGI,
		[CT_INSTR_ABSI]       = &&HANDLER_ABSI,

		[CT_INSTR_DIVU]       = &&HANDLER_DIVU,
		[CT_INSTR_MODU]       = &&HANDLER_MODU,

		[CT_INSTR_INC]       =  &&HANDLER_INC,
		[CT_INSTR_DEC]       =  &&HANDLER_DEC,

		[CT_INSTR_ADDF]       = &&HANDLER_ADDF,
		[CT_INSTR_SUBF]       = &&HANDLER_SUBF,
		[CT_INSTR_MULF]       = &&HANDLER_MULF,
		[CT_INSTR_DIVF]       = &&HANDLER_DIVF,
		[CT_INSTR_NEGF]       = &&HANDLER_NEGF,
		[CT_INSTR_ABSF]       = &&HANDLER_ABSF,

		[CT_INSTR_LOGIC_AND]  = &&HANDLER_LOGIC_AND,
		[CT_INSTR_LOGIC_OR]   = &&HANDLER_LOGIC_OR,
		[CT_INSTR_LOGIC_NOT]  = &&HANDLER_LOGIC_NOT,
		[CT_INSTR_LOGIC_XOR]  = &&HANDLER_LOGIC_XOR,

		[CT_INSTR_BIT_AND]    = &&HANDLER_BIT_AND,
		[CT_INSTR_BIT_OR]     = &&HANDLER_BIT_OR,
		[CT_INSTR_BIT_NOT]    = &&HANDLER_BIT_NOT,
		[CT_INSTR_BIT_XOR]    = &&HANDLER_BIT_XOR,
		[CT_INSTR_BIT_SHL]    = &&HANDLER_BIT_SHL,
		[CT_INSTR_BIT_SHR]    = &&HANDLER_BIT_SHR,
		[CT_INSTR_BIT_SHRA]   = &&HANDLER_BIT_SHRA,

		[CT_INSTR_CMPI]       = &&HANDLER_CMPI,
		[CT_INSTR_CMPU]       = &&HANDLER_CMPU,
		[CT_INSTR_CMPF]       = &&HANDLER_CMPF,

		[CT_INSTR_EQ]         = &&HANDLER_EQ,
		[CT_INSTR_NOT_EQ]     = &&HANDLER_NOT_EQ,
		[CT_INSTR_LESS]       = &&HANDLER_LESS,
		[CT_INSTR_LESS_EQ]    = &&HANDLER_LESS_EQ,
		[CT_INSTR_GREATER]    = &&HANDLER_GREATER,
		[CT_INSTR_GREATER_EQ] = &&HANDLER_GREATER_EQ,

		[CT_INSTR_JMP]        = &&HANDLER_JMP,
		[CT_INSTR_JMP_EQ]     = &&HANDLER_JMP_EQ,
		[CT_INSTR_JMP_NE]     = &&HANDLER_JMP_NE,
		[CT_INSTR_JMP_GT]     = &&HANDLER_JMP_GT,
		[CT_INSTR_JMP_GE]     = &&HANDLER_JMP_GE,
		[CT_INSTR_JMP_LT]     = &&HANDLER_JMP_LT,
		[CT_INSTR_JMP_LE]     = &&HANDLER_JMP_LE,
		[CT_INSTR_JMP_IF]     = &&HANDLER_JMP_IF,
		[CT_INSTR_JMP_IFNOT]  = &&HANDLER_JMP_IFNOT,

		[CT_INSTR_CALL]       = &&HANDLER_CALL,
		[CT_INSTR_RETURN]     = &&HANDLER_RETURN,
		[CT_INSTR_RETURN_VAL] = &&HANDLER_RETURN_VAL,

		[CT_INSTR_OBJ_CREATE]    = &&HANDLER_OBJ_CREATE,
		[CT_INSTR_OBJ_SIZE]      = &&HANDLER_OBJ_SIZE,
		[CT_INSTR_OBJ_GET]       = &&HANDLER_OBJ_GET,
		[CT_INSTR_OBJ_SET]       = &&HANDLER_OBJ_SET,
		[CT_INSTR_OBJ_GET_BYTE]  = &&HANDLER_OBJ_GET_BYTE,
		[CT_INSTR_OBJ_SET_BYTE]  = &&HANDLER_OBJ_SET_BYTE,
		[CT_INSTR_OBJ_RESIZE]    = &&HANDLER_OBJ_RESIZE,
		[CT_INSTR_OBJ_COPY]      = &&HANDLER_OBJ_COPY,
	};

	for (uint32_t i = 0; i < sizeof(dispatch_table)/sizeof(dispatch_table[0]); i++) {
		if (dispatch_table[i] == NULL) {
			dispatch_table[i] = &&HANDLER_ILLEGAL_INSTRUCTION;
		}
	}

	CtInstrSize* instrs = engine->image.instruction_pool;

	uint8_t r1, r2, r3, r4;
	int16_t i16;
	int32_t i32;
	uint32_t u32;
	float f32;
	CtAtom a1, a2, a3;
	CtAtomType t1, t2, t3;
	CtTypedAtom typed_atom;
	
	NEXT();

HANDLER_NULL:

	#ifdef CT_CONF_FAIL_ON_NULL
	goto HANDLER_ILLEGAL_INSTRUCTION;
	#else		
	NEXT();
	#endif // CT_CONF_FAIL_ON_NULL

HANDLER_HALT:
	r1 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	ctx->exit_code = a1.as_uint;
	return;

HANDLER_OUT:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	_ct_out(r1, a1);
	NEXT();

HANDLER_MOV:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_move_atom(ctx, r2, r1);
	NEXT();

HANDLER_CAST_I2F:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_float=(double)a1.as_int}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_CAST_F2I:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);

	if (!isfinite(a1.as_float) || a1.as_float > INT64_MAX || a1.as_float < INT64_MIN) {
		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"Overflow", 
			"Unable to cast %f to int.",
			a1.as_float
		);
		return;
	};

	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_int=a1.as_float}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_CAST_U2F:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_float=(double)a1.as_uint}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_CAST_F2U:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);

	if (!isfinite(a1.as_float) || a1.as_float > UINT64_MAX || a1.as_float < 0) {
		CT_ERROR_ENGINE(
			ct_thread_error, 
			"Engine", 
			"Overflow", 
			"Unable to cast %f to uint.",
			a1.as_float
		);
		return;
	};

	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_int=a1.as_float}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_LOAD_I16:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, 2, &i16);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_int=(int16_t)ct_image_byteswap_u16(i16)}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_LOAD_I32:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, 4, &i32);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_int=(int32_t)ct_image_byteswap_u32(i32)}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_LOAD_U32:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, 4, &u32);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_uint=(uint32_t)ct_image_byteswap_u32(u32)}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_LOAD_F32:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, 4, &f32);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_float=ct_image_byteswap_f32(f32)}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_LOAD_BYTE:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_uint=r2}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_READ_I64:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, sizeof(u32), &u32);
	a1.as_int = *(int64_t*)ct_ctx_read_data(ctx, u32);
	ct_ctx_store_atom(ctx, r1, a1, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_READ_U64:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, sizeof(u32), &u32);
	a1.as_uint = *(uint64_t*)ct_ctx_read_data(ctx, u32);
	ct_ctx_store_atom(ctx, r1, a1, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_READ_F64:
	r1 = instrs[ctx->ip++];
	_ct_load_bytes(instrs, &ctx->ip, sizeof(u32), &u32);
	a1.as_float = *(double*)ct_ctx_read_data(ctx, u32);
	ct_ctx_store_atom(ctx, r1, a1, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_ADDI: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_int, +); 
	NEXT();

HANDLER_SUBI: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_int, -); 
	NEXT();

HANDLER_MULI:
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_int, *); 
	NEXT();

HANDLER_DIVI: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_int, /); 
	NEXT();

HANDLER_MODI: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_int, %); 
	NEXT();

HANDLER_NEGI: 
	CT_INSTR_UNARYOP(CT_ATOM_PRIMITIVE, as_int, -); 
	NEXT();

HANDLER_ABSI: 
	CT_INSTR_UNARYOP(CT_ATOM_PRIMITIVE, as_int, labs); 
	NEXT();

HANDLER_DIVU: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, /); 
	NEXT();

HANDLER_MODU: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, %); 
	NEXT();

HANDLER_INC: 
	r1 = instrs[ctx->ip++];
	_ct_inc_atom(ctx, r1);
	NEXT();

HANDLER_DEC: 
	r1 = instrs[ctx->ip++];
	_ct_dec_atom(ctx, r1);
	NEXT();

HANDLER_ADDF: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_float, +); 
	NEXT();

HANDLER_SUBF: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_float, -); 
	NEXT();

HANDLER_MULF: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_float, *); 
	NEXT();

HANDLER_DIVF: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_float, /); 
	NEXT();

HANDLER_NEGF:
	CT_INSTR_UNARYOP(CT_ATOM_PRIMITIVE, as_float, -); 
	NEXT();

HANDLER_ABSF: 
	CT_INSTR_UNARYOP(CT_ATOM_PRIMITIVE, as_float, fabs); 
	NEXT();

HANDLER_LOGIC_AND: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_bool, &&); 
	NEXT();

HANDLER_LOGIC_OR: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_bool, ||); 
	NEXT();

HANDLER_LOGIC_NOT:     
	CT_INSTR_UNARYOP(CT_ATOM_PRIMITIVE, as_bool, !); 
	NEXT();

HANDLER_LOGIC_XOR: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_bool, ^); 
	NEXT();

HANDLER_BIT_AND: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, &); 
	NEXT();

HANDLER_BIT_OR: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, |); 
	NEXT();

HANDLER_BIT_NOT: 
	CT_INSTR_UNARYOP(CT_ATOM_PRIMITIVE, as_uint, ~); 
	NEXT();

HANDLER_BIT_XOR: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, ^); 
	NEXT();

HANDLER_BIT_SHL: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, <<); 
	NEXT();

HANDLER_BIT_SHR: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_uint, >>); 
	NEXT();

HANDLER_BIT_SHRA: 
	CT_INSTR_BINARYOP(CT_ATOM_PRIMITIVE, as_int, >>); 
	NEXT();

HANDLER_CMPI: 
	CT_INSTR_CMP(CT_ATOM_PRIMITIVE, as_int); 
	NEXT();

HANDLER_CMPU: 
	CT_INSTR_CMP(CT_ATOM_PRIMITIVE, as_uint); 
	NEXT();

HANDLER_CMPF: 
	CT_INSTR_CMP(CT_ATOM_PRIMITIVE, as_float); 
	NEXT();

HANDLER_EQ: 
	CT_INSTR_CMP_RESOLVER(==);
	NEXT();

HANDLER_NOT_EQ: 
	CT_INSTR_CMP_RESOLVER(!=);
	NEXT();

HANDLER_LESS: 
	CT_INSTR_CMP_RESOLVER(<);
	NEXT();

HANDLER_LESS_EQ: 
	CT_INSTR_CMP_RESOLVER(<=);
	NEXT();

HANDLER_GREATER: 
	CT_INSTR_CMP_RESOLVER(>);
	NEXT();

HANDLER_GREATER_EQ: 
	CT_INSTR_CMP_RESOLVER(>=);
	NEXT();

HANDLER_JMP: 
	CT_INSTR_JMP(); 
	NEXT();

HANDLER_JMP_EQ:
	if (ctx->cmp_diff == 0) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_NE:
	if (ctx->cmp_diff != 0) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_GT:
	if (ctx->cmp_diff > 0) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_GE:
	if (ctx->cmp_diff >= 0) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_LT:
	if (ctx->cmp_diff < 0) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_LE:
	if (ctx->cmp_diff <= 0) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_IF:
	r1 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	if (a1.as_bool) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_JMP_IFNOT:
	r1 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	if (!a1.as_bool) { CT_INSTR_JMP(); NEXT(); }
	ctx->ip += 4;
	NEXT();

HANDLER_CALL:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	r3 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	ct_ctx_call_procedure(ctx, a1.as_uint, r2, r3);
	NEXT();

HANDLER_RETURN:
	ct_ctx_return_procedure(ctx, (CtAtom){.as_uint=0}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_RETURN_VAL:
	r1 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	ct_ctx_return_procedure(ctx, a1, t1);
	NEXT();

HANDLER_OBJ_CREATE:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	a2.as_object = (CtObject*) ct_obj_create(&ctx->objects, a1.as_uint);
	ct_ctx_store_atom(ctx, r1, a2, CT_ATOM_OBJECT);
	NEXT();

HANDLER_OBJ_SIZE:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	CT_CHECK_IF_OBJECT(t1);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_uint = a1.as_object->size}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_OBJ_GET:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	r3 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	ct_ctx_load_atom(ctx, r3, &a2, &t2);
	CT_CHECK_IF_OBJECT(t1);
	typed_atom = ct_obj_get(&ctx->objects, a1.as_object, a2.as_uint);
	ct_ctx_store_atom(ctx, r1, typed_atom.atom, typed_atom.type);
	NEXT();

HANDLER_OBJ_SET:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	r3 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	ct_ctx_load_atom(ctx, r2, &a2, &t2);
	ct_ctx_load_atom(ctx, r3, &a3, &t3);
	CT_CHECK_IF_OBJECT(t1);
	ct_obj_set(&ctx->objects, a1.as_object, a2.as_uint, (CtTypedAtom){t3, a3});
	NEXT();

HANDLER_OBJ_GET_BYTE:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	r3 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a1, &t1);
	ct_ctx_load_atom(ctx, r3, &a2, &t2);
	CT_CHECK_IF_OBJECT(t1);
	ct_ctx_store_atom(ctx, r1, (CtAtom){.as_uint=ct_obj_get_byte(&ctx->objects, a1.as_object, a2.as_uint)}, CT_ATOM_PRIMITIVE);
	NEXT();

HANDLER_OBJ_SET_BYTE:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	r3 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	ct_ctx_load_atom(ctx, r2, &a2, &t2);
	ct_ctx_load_atom(ctx, r3, &a3, &t3);
	CT_CHECK_IF_OBJECT(t1);
	ct_obj_set_byte(&ctx->objects, a1.as_object, a2.as_uint, a3.as_uint);
	NEXT();

HANDLER_OBJ_RESIZE:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r1, &a1, &t1);
	ct_ctx_load_atom(ctx, r2, &a2, &t2);
	CT_CHECK_IF_OBJECT(t1);
	ct_obj_resize(&ctx->objects, a1.as_object, a2.as_uint);
	NEXT();

HANDLER_OBJ_COPY:
	r1 = instrs[ctx->ip++];
	r2 = instrs[ctx->ip++];
	ct_ctx_load_atom(ctx, r2, &a2, &t2);
	CT_CHECK_IF_OBJECT(t2);
	a1.as_object = (CtObject*) ct_obj_copy(&ctx->objects, a2.as_object);
	ct_ctx_store_atom(ctx, r1, a1, CT_ATOM_OBJECT);
	NEXT();

HANDLER_ILLEGAL_INSTRUCTION:
	CT_ERROR_ENGINE(
		ct_thread_error,
		"Engine",
		"IllegalInstruction",
		"0x%x",
		instrs[--ctx->ip]
	);
	return;
}
