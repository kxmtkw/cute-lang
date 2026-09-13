from Compiler.codegen.state import GeneratorState
from Compiler.defs.nodes import NodeVisitor, Node
from Compiler.imagen.image import ImageBuilder
from Compiler.imagen.program import Program, Procedure, Label, Constant, Instruction, InstrSet
from Compiler.imagen.image import Format


OUT_FMT: dict[str, int] = {
	"binary": 0,
	"hex": 1,
	"int": 2,
	"uint": 3,
	"float": 4,
	"bool": 5,
	"char": 6,
	"object": 7
}


class BuiltinHandler:


	def __init__(self, state: GeneratorState, builder: ImageBuilder, program: Program) -> None:
		self.state = state
		self.program = program
		self.builder = builder

		self.handler_dispatch = {
			"out": self.builtin_out,
			"instr": self.builtin_instr,
		}

		self.current_handler_arguments = []


	def handle(self, builtin_call: Node.BuiltinCommand):
		if len(builtin_call.args) == 0:
			return
			
		handler = builtin_call.args[0]

		if not isinstance(handler, Node.Identifier):
			raise ValueError("__builtin__ handler can only be a word.")

		if handler.value not in self.handler_dispatch:
			raise ValueError(f"Unknown __builtin__ handler: {handler.value}")

		self.current_handler_arguments = builtin_call.args[1:] if len(builtin_call.args) >= 2 else []

		self.handler_dispatch[handler.value]()


	def builtin_out(self):

		if len(self.current_handler_arguments) != 2:
			raise ValueError(f"__builtin__ out requires 2 arguments.")

		fmt = self.current_handler_arguments[0]
		slot = self.current_handler_arguments[1]

		if isinstance(fmt, Node.Identifier):
			fmt_code = OUT_FMT.get(fmt.value, OUT_FMT["hex"])
		else:
			raise ValueError("Expected a fmt code for arg 1 of __builtin__ out.")

		if isinstance(slot, Node.Identifier):
			slot_num = self._encode_instruction_argument(slot, Format.u8, 0)
		else:
			raise ValueError("Expected an identifier for arg 2 of __builtin__ out.")


		out = Instruction(InstrSet.out, [fmt_code, slot_num])
		self.state.current_procedure.instructions.append(out)


	def builtin_instr(self):

		if not self.current_handler_arguments:
			raise ValueError("__builtin__ instr requires an instruction name.")

		instruction_name = self.current_handler_arguments[0]
		if not isinstance(instruction_name, Node.Identifier):
			raise ValueError("Expected an instruction name for __builtin__ instr.")

		instruction = InstrSet.__members__.get(instruction_name.value)
		if instruction is None:
			raise ValueError(f"Unknown instruction for __builtin__ instr: {instruction_name.value}")

		arguments = self.current_handler_arguments[1:]
		_, argument_formats = instruction.value
		expected_argument_count = len(argument_formats)
		if len(arguments) != expected_argument_count:
			raise ValueError(
				f"__builtin__ instr {instruction.name} requires {expected_argument_count} arguments; "
				f"got {len(arguments)}."
			)

		encoded_arguments = [
			self._encode_instruction_argument(argument, argument_formats[index], index + 1)
			for index, argument in enumerate(arguments)
		]
		self.state.current_procedure.instructions.append(Instruction(instruction, encoded_arguments))


	def _encode_instruction_argument(self, argument: Node.Expression, fmt: Format, position: int):
		
		if isinstance(argument, Node.Identifier):
			if fmt != Format.u8:
				raise ValueError(
					f"Argument {position} of __builtin__ instr must be a literal for format {fmt.value}."
				)

			assert argument.n_refers is not None
			assert isinstance(argument.n_refers, Node.Declaration)
			assert argument.n_refers.c_slot_id is not None
			slot_num = argument.n_refers.c_slot_id
			return slot_num

		if isinstance(argument, Node.Literal):
			if isinstance(argument.value, (int, float)):
				return argument.value
			if isinstance(argument.value, (bool)):
				return int(argument.value)
			if isinstance(argument.value, str):
				return ord(argument.value)

		raise ValueError(f"Argument {position} of __builtin__ instr must be an identifier or literal.")
