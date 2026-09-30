#ifndef CUTE_INSTR_H
#define CUTE_INSTR_H


#include <stdint.h>


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

    CT_INSTR_OBJ_CREATE     = 0xC0,
    CT_INSTR_OBJ_SIZE       = 0xC1,
    CT_INSTR_OBJ_GET        = 0xC2,
    CT_INSTR_OBJ_SET        = 0xC3,
	CT_INSTR_OBJ_GET_BYTE   = 0xC4,
	CT_INSTR_OBJ_SET_BYTE   = 0xC5,
	CT_INSTR_OBJ_RESIZE     = 0xC6,
	CT_INSTR_OBJ_COPY       = 0xC7,

} CtInstr;

// All instructions should be able to fit inside this. Allows for 256 different instructions
typedef uint8_t CtInstrSize;


#endif // CUTE_INSTR_H