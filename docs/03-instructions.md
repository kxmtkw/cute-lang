
# Cute Instruction Set

The cute instruction set defines the following listed instruction. Each instruction's assembler representation and its implementation in the engine is also listed.
Each `$_` signs represents an arbitrary slot. `immX` where X is a number, represents direct bits in the bytecode. For example, `imm32` represents 4 continuous bytes.

---

#### CT_INSTR_NULL        `0x00`
Assembler Repr: `null`
```
null
```
Does absolutely nothing. Can be used as safe compiler placeholders. The engine can be configured to fail on null instructions as well.

---

#### CT_INSTR_HALT        `0x01`
Assembler Repr: `halt`
```
halt $x
```
Causes the engine to halt/exit. $x stores the exit code.

---

#### CT_INSTR_OUT         `0x02`
Assembler Repr: `out`
```
out imm8 $x
```
Outputs the current value of the referred slot. The first byte holds the format and can be:
- 0 : binary
- 1 : hexadecimal
- 2 : int
- 3 : unsigned int (uint)
- 4 : float
- 5 : bool
- 6 : object
- _ : defaults to hexadecimal

This is mostly for debugging.

---

#### CT_INSTR_MOV         `0x20`
Assembler Repr: `mov`
```
mov $x $y // $y -> $x
```
Moves (or rather copies) data from $y to $x.

---

#### CT_INSTR_LOAD_I16        `0x21`
Assembler Repr: `loadi16`
```
loadi16 $x imm16 // imm16 -> $x
```
Reads an int and writes the value to $x.

---

#### CT_INSTR_LOAD_I32        `0x22`
Assembler Repr: `loadi32`
```
loadi32 $x imm32 // imm32 -> $x
```
Reads an int and writes the value to $x.

---

#### CT_INSTR_LOAD_U32        `0x23`
Assembler Repr: `loadu32`
```
loadu32 $x imm32 // imm32 -> $x
```
Reads an uint and writes the value to $x.

---

#### CT_INSTR_LOAD_F32        `0x24`
Assembler Repr: `loadf32`
```
loadf32 $x imm32 // imm32 -> $x
```
Reads an int and writes the value to $x.

---

#### CT_INSTR_LOAD_BYTE        `0x25`
Assembler Repr: `loadbyte`
```
loadbyte $x imm8 // imm8 -> $x
```
Reads a single byte and writes the value to $x.

---

#### CT_INSTR_READ_I64        `0x26`
Assembler Repr: `readi64`
```
readi64 $x imm32 // imm64 -> $x
```
Loads an i64 from the data section with offset imm32.

---

#### CT_INSTR_READ_U64        `0x27`
Assembler Repr: `readu64`
```
readu64 $x imm32 // imm64 -> $x
```
Loads an u64 from the data section with offset imm32.

---

#### CT_INSTR_READ_F64        `0x28`
Assembler Repr: `readf64`
```
readf64 $x imm32 // imm64 -> $x
```
Loads an f64 from the data section with offset imm32.

---

#### CT_INSTR_CAST_I2F    `0x2A`
Assembler Repr: `i2f`
```
i2f $x $y
```
Casts an int from $y to a float to $x. Casts normally, never fails.

---

#### CT_INSTR_CAST_F2I    `0x2B`
Assembler Repr: `f2i`
```
f2i $x $y
```
Casts a float from $y to an int to $x. Fails to cast the float if it exceeds the size of an int or is nan/inf.

---

#### CT_INSTR_CAST_U2F    `0x2C`
Assembler Repr: `u2f`
```
u2f $x $y
```
Casts an uint from $y to a float to $x. Never fails.

---

#### CT_INSTR_CAST_F2U    `0x2D`
Assembler Repr: `f2u`
```
f2u $x $y
```
Casts a float from $y to an uint to $x. Fails to cast the float if it exceeds the size of an uint or is nan/inf.

---

#### CT_INSTR_ADDI        `0x30`
Assembler Repr: `addi`

#### CT_INSTR_SUBI        `0x31`
Assembler Repr: `subi`

#### CT_INSTR_MULI        `0x32`
Assembler Repr: `muli`

#### CT_INSTR_DIVI        `0x33`
Assembler Repr: `divi`

#### CT_INSTR_MODI        `0x34`
Assembler Repr: `modi`

#### CT_INSTR_NEGI        `0x35`
Assembler Repr: `negi`

#### CT_INSTR_ABSI        `0x36`
Assembler Repr: `absi`

#### CT_INSTR_DIVU        `0x37`
Assembler Repr: `divu`

#### CT_INSTR_MODU        `0x38`
Assembler Repr: `modu`

#### CT_INSTR_INC         `0x3A`
Assembler Repr: `inc`

#### CT_INSTR_DEC         `0x3B`
Assembler Repr: `dec`

#### CT_INSTR_ADDF        `0x50`
Assembler Repr: `addf`

#### CT_INSTR_SUBF        `0x51`
Assembler Repr: `subf`

#### CT_INSTR_MULF        `0x52`
Assembler Repr: `mulf`

#### CT_INSTR_DIVF        `0x53`
Assembler Repr: `divf`

#### CT_INSTR_NEGF        `0x54`
Assembler Repr: `negf`

#### CT_INSTR_ABSF        `0x55` 
Assembler Repr: `absf`   

#### CT_INSTR_LOGIC_AND   `0x60`
Assembler Repr: `and`

#### CT_INSTR_LOGIC_OR    `0x61`
Assembler Repr: `or`

#### CT_INSTR_LOGIC_NOT   `0x62`
Assembler Repr: `not`

#### CT_INSTR_LOGIC_XOR   `0x63`
Assembler Repr: `xor`

#### CT_INSTR_BIT_AND     `0x70`
Assembler Repr: `band`

#### CT_INSTR_BIT_OR      `0x71`
Assembler Repr: `bor`

#### CT_INSTR_BIT_NOT     `0x73`
Assembler Repr: `not`

#### CT_INSTR_BIT_XOR     `0x74`
Assembler Repr: `bxor`

#### CT_INSTR_BIT_SHL     `0x75`
Assembler Repr: `bshl`

#### CT_INSTR_BIT_SHR     `0x76` 
Assembler Repr: `bshr`

#### CT_INSTR_BIT_SHRA    `0x77` 
Assembler Repr: `bshra`

--- 

All the above instructions are similar. They include arithmetic, logic and bitwise operations. They do not check types but do overwrite if the slot holds an `object` atom.

Above operations are either unary:
```
unary $x $y // $y -> $x
```
or binary:
```
binary $x $y $z // $y * $z -> $x
```
In both cases, $x is the destination slot.

---

#### CT_INSTR_CMPI        `0x80`
Assembler Repr: `cmpi`

#### CT_INSTR_CMPU        `0x81`
Assembler Repr: `cmpu`

#### CT_INSTR_CMPF        `0x82`
Assembler Repr: `cmpf`

---

Compares two values.
```
cmp $x $y // $x - $y
```
No destination slot for the cmp instructions because the result is stored in a hidden flag.
To make use of this result, either one of the cmp resolvers should be used which turn the flag into a boolean value or the one of the jump instructions which read from the flag directly.

---

#### CT_INSTR_EQ          `0x90`
Assembler Repr: `eq`

#### CT_INSTR_NOT_EQ      `0x91`
Assembler Repr: `neq`

#### CT_INSTR_LESS        `0x92`
Assembler Repr: `lt`

#### CT_INSTR_LESS_EQ     `0x93`
Assembler Repr: `lteq`

#### CT_INSTR_GREATER     `0x94`
Assembler Repr: `gt`

#### CT_INSTR_GREATER_EQ  `0x95`
Assembler Repr: `gteq`

---
Turns the cmp flag into a boolean value.
```
cmp-resolver $x
```
Where $x now stores the cmp flag represented as a boolean value.

---

#### CT_INSTR_JMP         `0xA0`
Assembler Repr: `jmp`
```
jmp imm32
```
Makes an unconditional jump by changing the program counter. The jump is offset based.

---

#### CT_INSTR_JMP_EQ      `0xA1`
Assembler Repr: `jmpeq`

#### CT_INSTR_JMP_NE      `0xA2`
Assembler Repr: `jmpne`

#### CT_INSTR_JMP_GT      `0xA3`
Assembler Repr: `jmpgt`

#### CT_INSTR_JMP_GE      `0xA4`
Assembler Repr: `jmpge`

#### CT_INSTR_JMP_LT      `0xA5`
Assembler Repr: `jmplt`

#### CT_INSTR_JMP_LE      `0xA6`
Assembler Repr: `jmple`

--- 

Make a conditional jump by reading from the cmp flag directly.
```
jmp imm32
```

---

#### CT_INSTR_JMP_IF      `0xA7`
Assembler Repr: `jmpif`

#### CT_INSTR_JMP_IFNOT    `0xA8`
Assembler Repr: `jmpifn`

---

Read a boolean value from a slot and jump depending on satisfied condition.
```
jmp $x imm32
```

---


#### CT_INSTR_CALL        `0xB0`
Assembler Repr: `call`

Call a procedure.
```
call $x $y $z // procedures[$x]($y...) -> $z
```
The slot $x holds the id of the procedure to be called.

The slot $y indicates the starting slot from which the arguments are read. 
For example, if a procedure requires 5 arguments and $y is $10, then the values of $10-$14 will be passed to the procedure. 

The slot $z indicates the slot to which the return value of the called procedure should be written.

Each procedure has its own 256 slots.

--- 

#### CT_INSTR_RETURN      `0xB1`
Assembler Repr: `ret`

Return from a procedure to the caller. Implicitly returns 0 back to the caller.

```
ret
```

--- 

#### CT_INSTR_RETURN_VAL  `0xB2`
Assembler Repr: `retval`

Return from a procedure while also returning a value to the caller.

```
retval $x
```

Returns whatever is present in $x. 

> Returning from procedure 0 (if it is the first procedure called and is not recursively called again) has the same effect as `CT_INSTR_HALT`

---

#### CT_INSTR_MOD_CALL    `0xBA`
Assembler Repr: `modcall`
```
modcall $x $y $z $a;
```
Make a module call. $x holds the module id, $y holds the method id, $z is the argument start slot and $a is the return slot.

---

#### CT_INSTR_CON_NEW     `0xC0`
Assembler Repr: `connew`

Allocate a new container of specific size.
```
connew $x $y
```
The slot $y indicates the size of the slot while $x is destination slot.

---

#### CT_INSTR_CON_GET     `0xC1`
Assembler Repr: `conget`

Get an atom from a container.
```
conget $x $y $z
```
Where $x is the destination slot, $y is the container, $z is the index to be accessed. 

---

#### CT_INSTR_CON_SET     `0xC2`
Assembler Repr: `conset`

Set an atom in a container.
```
conset $x $y $z
```
Where $x is the container, $y is the index, $z is the atom to be stored. 

--- 

#### CT_INSTR_CON_SIZE    `0xC3`
Assembler Repr: `consize`

Get the size of a container.
```
consize $x $y
```
Where $x is the dest and $y is the container. 

---

#### CT_INSTR_CON_COPY    `0xC4`
Assembler Repr: `concopy`

Create a shallow copy of a container.
```
concopy $x $y
```

---