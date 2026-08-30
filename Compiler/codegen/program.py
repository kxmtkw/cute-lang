from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any

from Compiler.codegen.image import ImageBuilder, Format


class InstrSet(Enum):
	null     = (0x00, [])
	halt     = (0x01, [Format.u8])
	out      = (0x02, [Format.u8, Format.u8])

	mov      = (0x20, [Format.u8, Format.u8])
	loadi16  = (0x21, [Format.u8, Format.i16])
	loadi32  = (0x22, [Format.u8, Format.i32])
	loadu32  = (0x23, [Format.u8, Format.u32])
	loadf32  = (0x24, [Format.u8, Format.f32])
	loadbyte = (0x25, [Format.u8, Format.u8])
	readi64  = (0x26, [Format.u8, Format.u32])
	readu64  = (0x27, [Format.u8, Format.u32])
	readf64  = (0x28, [Format.u8, Format.u32])
	i2f      = (0x2A, [Format.u8, Format.u8])
	f2i      = (0x2B, [Format.u8, Format.u8])
	u2f      = (0x2C, [Format.u8, Format.u8])
	f2u      = (0x2D, [Format.u8, Format.u8])

	addi     = (0x30, [Format.u8, Format.u8, Format.u8])
	subi     = (0x31, [Format.u8, Format.u8, Format.u8])
	muli     = (0x32, [Format.u8, Format.u8, Format.u8])
	divi     = (0x33, [Format.u8, Format.u8, Format.u8])
	modi     = (0x34, [Format.u8, Format.u8, Format.u8])
	negi     = (0x35, [Format.u8, Format.u8])
	absi     = (0x36, [Format.u8, Format.u8])
	divu     = (0x37, [Format.u8, Format.u8, Format.u8])
	modu     = (0x38, [Format.u8, Format.u8, Format.u8])
	inc      = (0x3A, [Format.u8])
	dec      = (0x3B, [Format.u8])

	addf     = (0x50, [Format.u8, Format.u8, Format.u8])
	subf     = (0x51, [Format.u8, Format.u8, Format.u8])
	mulf     = (0x52, [Format.u8, Format.u8, Format.u8])
	divf     = (0x53, [Format.u8, Format.u8, Format.u8])
	negf     = (0x54, [Format.u8, Format.u8])
	absf     = (0x55, [Format.u8, Format.u8])

	and_     = (0x60, [Format.u8, Format.u8, Format.u8])
	or_      = (0x61, [Format.u8, Format.u8, Format.u8])
	not_     = (0x62, [Format.u8, Format.u8])
	xor      = (0x63, [Format.u8, Format.u8, Format.u8])
	band     = (0x70, [Format.u8, Format.u8, Format.u8])
	bor      = (0x71, [Format.u8, Format.u8, Format.u8])
	bnot     = (0x73, [Format.u8, Format.u8])
	bxor     = (0x74, [Format.u8, Format.u8, Format.u8])
	bshl     = (0x75, [Format.u8, Format.u8, Format.u8])
	bshr     = (0x76, [Format.u8, Format.u8, Format.u8])
	bshra    = (0x77, [Format.u8, Format.u8, Format.u8])

	cmpi     = (0x80, [Format.u8, Format.u8])
	cmpu     = (0x81, [Format.u8, Format.u8])
	cmpf     = (0x82, [Format.u8, Format.u8])
	eq       = (0x90, [Format.u8])
	ne       = (0x91, [Format.u8])
	lt       = (0x92, [Format.u8])
	le       = (0x93, [Format.u8])
	gt       = (0x94, [Format.u8])
	ge       = (0x95, [Format.u8])

	jmp      = (0xA0, [Format.i32])
	jmpeq    = (0xA1, [Format.i32])
	jmpne    = (0xA2, [Format.i32])
	jmpgt    = (0xA3, [Format.i32])
	jmpge    = (0xA4, [Format.i32])
	jmplt    = (0xA5, [Format.i32])
	jmple    = (0xA6, [Format.i32])
	jmpif    = (0xA7, [Format.u8, Format.i32])
	jmpifn   = (0xA8, [Format.u8, Format.i32])

	call     = (0xB0, [Format.u8, Format.u8, Format.u8])
	ret      = (0xB1, [])
	retval   = (0xB2, [Format.u8])
	modcall  = (0xBA, [Format.u8, Format.u8, Format.u8, Format.u8])

	connew   = (0xC0, [Format.u8, Format.u8])
	conget   = (0xC1, [Format.u8, Format.u8, Format.u8])
	conset   = (0xC2, [Format.u8, Format.u8, Format.u8])
	consize  = (0xC3, [Format.u8, Format.u8])
	concopy  = (0xC4, [Format.u8, Format.u8])


class CompileableUnit(ABC):

	def __init__(self) -> None:
		pass

	@abstractmethod
	def assemble(self, builder: ImageBuilder):
		pass


class ReferenceUnit(ABC):

	def __init__(self) -> None:
		pass

	@abstractmethod
	def refer(self, builder: ImageBuilder) -> str:
		pass


@dataclass
class Instruction(CompileableUnit):
	opcode: InstrSet
	arguments: list[int | float | "ReferenceUnit"]

	def __repr__(self) -> str:
		arguments = " ".join(
			repr(argument) for argument in self.arguments
		)
		return f"{self.opcode.name} {arguments}".rstrip()


	def assemble(self, builder: ImageBuilder):
		instruction, arg_fmts = self.opcode.value
		builder.add_to_instr_pool(Format.u8, instruction)

		if len(self.arguments) != len(arg_fmts):
			raise ValueError()
		
		for i in range(len(arg_fmts)):
			arg = self.arguments[i]

			if isinstance(arg, ReferenceUnit):
				fmt = arg.refer(builder)

				if fmt != arg_fmts[i]:
					raise ValueError(f"Incompatible reference unit. Cannot write {fmt} in place of {arg_fmts[i]}")
				continue

			builder.add_to_instr_pool(arg_fmts[i], arg)


@dataclass
class Label(CompileableUnit, ReferenceUnit):
	id: int

	def __repr__(self) -> str:
		return f"L{self.id}:"

	def assemble(self, builder: ImageBuilder):
		builder.mark_label(self.id)		

	def refer(self, builder: ImageBuilder) -> str:
		builder.refer_label(self.id)
		builder.add_to_instr_pool(Format.i32, 0)
		return Format.i32


@dataclass
class Constant(CompileableUnit, ReferenceUnit):
	value: int | float | bytes
	fmt: str

	def __repr__(self) -> str:
		return f"Constant {self.fmt} {self.value!r}"

	def assemble(self, builder: ImageBuilder):
		self._offset = builder.add_to_data_blob(self.fmt, self.value)

	def refer(self, builder: ImageBuilder) -> str:

		if not hasattr(self, "_offset"):
			raise ValueError(f"{self} not registered yet. Does not have offset!")
		
		builder.add_to_instr_pool(Format.u32, self._offset)
		return Format.u32


@dataclass
class Procedure(CompileableUnit):
	id: int
	argument_count: int
	instructions: list[Instruction | Label]

	def __repr__(self) -> str:
		instructions = "\n".join(repr(instruction) for instruction in self.instructions)
		header = f"-- Procedure {self.id} {self.argument_count}"
		return f"{header}\n\n{instructions}"

	def assemble(self, builder: ImageBuilder):
		builder.clear_labels()
		builder.new_proc(self.id, self.argument_count)
		for instr in self.instructions:
			instr.assemble(builder)
		builder.resolve_labels()


@dataclass
class Program(CompileableUnit):
	constants: list[Constant]
	procedures: list[Procedure]

	def __repr__(self) -> str:
		header = "- Program\n"
		units = [*self.constants, *self.procedures]
		return header + "\n".join(repr(unit) for unit in units)

	def assemble(self, builder: ImageBuilder):

		for const in self.constants:
			const.assemble(builder)

		for proc in self.procedures:
			proc.assemble(builder)


	
