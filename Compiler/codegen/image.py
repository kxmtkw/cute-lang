import struct
from enum import Enum


MAGIC_ID = 0x63757465

class Format:
	i8 = "<b"
	u8 = "<B"
	i16 = "<h"
	u16 = "<H"
	i32 = "<i"
	u32 = "<I"
	f32 = "<f"
	i64 = "<q"
	u64 = "<Q"
	f64 = "<d"
	str = lambda l: f"{l}s"

HEADER_FORMAT = "<IHHHxxIII"


class ImageBuilder:


	def __init__(self):
		
		self.magic = MAGIC_ID
		self.version: tuple[int, int, int] = (1, 0, 0)

		self.data_blob = bytearray()

		self.procedure_table = bytearray()
		self.procedure_count = 0

		self.instruction_pool = bytearray()

		self.label_addresses: dict[int, int] = {} # label id to label address
		self.label_references: dict[int, int] = {} # reference address to label id


	def new_proc(self, procedure_id: int, arg_count: int) -> int:
		
		procedure_size = 8

		if procedure_id < 0:
			raise ValueError("procedure_id must be non-negative")

		bytecode_index = len(self.instruction_pool)
		required_size = (procedure_id + 1) * procedure_size
		if required_size > len(self.procedure_table):
			self.procedure_table.extend(b"\x00" * (required_size - len(self.procedure_table)))

		struct.pack_into("<II", self.procedure_table, procedure_id * procedure_size, bytecode_index, arg_count)
		self.procedure_count = len(self.procedure_table) // procedure_size
		return bytecode_index


	def get_address(self) -> int:
		return len(self.instruction_pool)


	def add_to_instr_pool(self, fmt: str, value: int | float) -> int:
		offset = len(self.instruction_pool)
		self.instruction_pool.extend(struct.pack(fmt, value))
		return offset


	def mark_label(self, label_id: int):
		if label_id in self.label_addresses:
			raise ValueError(f"Jump already registered: {label_id}")
		self.label_addresses[label_id] = self.get_address()


	def refer_label(self, label_id: int):
		self.label_references[self.get_address()] = label_id


	def resolve_labels(self):

		for refr_address, label in self.label_references.items():
			if label not in self.label_addresses:
				print(label)
				print(self.label_addresses)
				raise ValueError()

			label_address = self.label_addresses[label]

			offset = label_address - (refr_address + 4)

			self.insert_to_instr_pool(Format.i32, offset, refr_address)


	def clear_labels(self):
		self.label_addresses.clear()
		self.label_references.clear()


	def insert_to_instr_pool(self, fmt: str, value: int | float, address: int) -> None:
		packed_bytes = struct.pack(fmt, value)
		for i in range(len(packed_bytes)):
			self.instruction_pool[address + i] = packed_bytes[i]


	def add_to_data_blob(self, fmt: str, value: int | float | bytes) -> int:
		offset = len(self.data_blob)		
		self.data_blob.extend(struct.pack(fmt, value))
		return offset


	def compile(self) -> bytes:
		major, minor, patch = self.version
		header = struct.pack(
			HEADER_FORMAT,
			self.magic,
			major,
			minor,
			patch,
			len(self.data_blob),
			self.procedure_count,
			len(self.instruction_pool),
		)
		return b"".join((header, self.data_blob, self.procedure_table, self.instruction_pool))

	
