import struct
from enum import Enum

MAGIC_ID = 0x63757465 # spells out cute
HEADER_FORMAT = "<7I"

class Format(Enum):
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


class ImageBuilder:

	def __init__(self):
		
		self.magic = MAGIC_ID
		self.version: tuple[int, int, int] = (1, 0, 0)

		self.data_blob = bytearray()
		self.procedure_table = bytearray()
		self.instruction_pool = bytearray()

		self.procedure_count = 0

		self.label_addresses: dict[int, int] = {} # label id to label address
		self.label_references: dict[int, int] = {} # reference address to label id


	def new_proc(self, procedure_id: int, arg_count: int) -> int:
		"""
		Start a new procedure declaration. All proceeding instructions will belong to this procedure.
		Also clears the previous labels.
		Returns the bytecode address of the procedure.
		"""

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


	def end_procedure(self):
		"End the current procedure, resolving all label references."
		self.resolve_labels()
		self.clear_labels()


	def get_address(self) -> int:
		"Get the current address (basically the current size of the instruction pool)."
		return len(self.instruction_pool)


	def add_to_instr_pool(self, fmt: Format, value: int | float) -> int:
		"Add an int/float to the instruction pool with the given format."
		offset = len(self.instruction_pool)
		self.instruction_pool.extend(struct.pack(fmt.value, value))
		return offset


	def insert_to_instr_pool(self, fmt: Format, value: int | float, address: int) -> None:
		"Insert an int/float to the instruction pool with the given format."
		packed_bytes = struct.pack(fmt.value, value)
		for i in range(len(packed_bytes)):
			self.instruction_pool[address + i] = packed_bytes[i]


	def mark_label(self, label_id: int):
		"At the current address, mark a labe"
		if label_id in self.label_addresses:
			raise ValueError(f"Label already registered: {label_id}")
		self.label_addresses[label_id] = self.get_address()


	def refer_label(self, label_id: int):
		"At the current address, register a label reference to be resolved later."
		self.label_references[self.get_address()] = label_id


	def resolve_labels(self):
		"Resolve all label references"

		for refr_address, label in self.label_references.items():
			if label not in self.label_addresses:
				raise ValueError(f"Label {label} not found.")

			label_address = self.label_addresses[label]

			offset = label_address - (refr_address + 4)

			self.insert_to_instr_pool(Format.i32, offset, refr_address)


	def clear_labels(self):
		"Clear all labels and label references."
		self.label_addresses.clear()
		self.label_references.clear()


	def add_to_data_blob(self, fmt: Format, value: int | float | bytes) -> int:
		"Add something to the data blob with a given format"
		offset = len(self.data_blob)		
		self.data_blob.extend(struct.pack(fmt.value, value))
		return offset


	def compile(self) -> bytes:
		"Stitch the image segments together to make a complete image."
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

	
