from Compiler.codegen.state import GeneratorState
from Compiler.parser.nodes import BinaryOpType, NodeVisitor, Node
from Compiler.codegen.image import ImageBuilder
from Compiler.codegen.program import Program, Procedure, Label, Constant, Instruction, InstrSet


OUT_FMT: dict[str, int] = {
	"binary": 0,
	"hex": 1,
	"int": 2,
	"uint": 3,
	"float": 4,
	"bool": 5,
	"object": 6
}


class BuiltinHandler:


	def __init__(self, state: GeneratorState, builder: ImageBuilder, program: Program) -> None:
		self.state = state
		self.program = program
		self.builder = builder

		self.handler_dispatch = {
			"out": self.builtin_out,
			"halt": self.builtin_halt
		}

		self.current_handler_arguments = []


	def handle(self, builtin_call: Node.Call):
		if len(builtin_call.args) == 0:
			return
			
		handler = builtin_call.args[0]

		if not isinstance(handler, Node.Identifier):
			raise ValueError("__builtin__ handler can only be a word.")

		if handler.name not in self.handler_dispatch:
			raise ValueError(f"Unknown __builtin__ handler: {handler.name}")

		self.current_handler_arguments = builtin_call.args[1:] if len(builtin_call.args) >= 2 else []

		self.handler_dispatch[handler.name]()


	def builtin_out(self):

		if len(self.current_handler_arguments) != 2:
			raise ValueError(f"__builtin__ out requires 2 arguments.")

		fmt = self.current_handler_arguments[0]
		slot = self.current_handler_arguments[1]

		if isinstance(fmt, Node.Identifier):
			fmt_code = OUT_FMT.get(fmt.name, OUT_FMT["hex"])
		else:
			raise ValueError("Expected a fmt code for arg 1 of __builtin__ out.")


		slot_num = self.state.get_variable_slot(slot.name)

		out = Instruction(InstrSet.out, [fmt_code, slot_num])
		self.state.current_procedure.instructions.append(out)


	def builtin_halt(self):

		if len(self.current_handler_arguments) != 1:
			raise ValueError(f"__builtin__ halt requires 1 argument.")

		slot = self.current_handler_arguments[0]

		slot_num = self.state.get_variable_slot(slot.name)

		halt = Instruction(InstrSet.halt, [slot_num])
		self.state.current_procedure.instructions.append(halt)