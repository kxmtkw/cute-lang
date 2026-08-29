from Compiler.parser.nodes import BinaryOpType, NodeVisitor, Node
from Compiler.codegen.image import ImageBuilder
from Compiler.codegen.program import Program, Procedure, Label, Constant, Instruction, InstrSet


SLOT_COUNT = 256


class GeneratorState:


	def __init__(self) -> None:
		self._current_procedure: Procedure | None = None
		self._proc_slots: list[bool] = []
		self._temp_slots: list[int] = []
		self._variable_assignments: dict[str, int] = {} # variable name to slot


	def new_procedure(self, proc: Procedure):
		if self._current_procedure is not None:
			raise ValueError()
		self._current_procedure = proc
		self._proc_slots = [False for slot in range(SLOT_COUNT)]
		self._variable_assignments.clear()


	def end_procedure(self):
		if self._current_procedure is None:
			raise ValueError()
		self._current_procedure = None


	@property
	def current_procedure(self) -> Procedure:
		if self._current_procedure is None:
			raise ValueError("current_procedure not assigned yet.")
		return self._current_procedure


	def get_slot(self) -> int | None:
		for i, slot in enumerate(self._proc_slots):
			if not slot:
				self._proc_slots[i] = True
				return i
		return None


	def free_slot(self, slot: int):
		self._proc_slots[slot] = False


	def push_temp_slot(self, slot: int):
		self._temp_slots.append(slot)


	def pop_temp_slot(self) -> int:
		return self._temp_slots.pop()


	def set_variable_slot(self, name: str, slot: int):
		self._variable_assignments[name] = slot


	def get_variable_slot(self, name: str) -> int:
		return self._variable_assignments[name]




class CodeGenerator(NodeVisitor):

	def __init__(self) -> None:
		super().__init__()
		self.state = GeneratorState()
		self.builder = ImageBuilder()
		self.program = Program([], [])

	
	def visitProgram(self, node: Node.Program):
		for func in node.statements:
			self.visit(func)

		self.program.assemble(self.builder)
		image = self.builder.compile()
		with open("dev/test.cute", "wb") as file:
			file.write(image)


	def visitFunction(self, node: Node.Function):
		proc = Procedure(0, 0, [])

		self.state.new_procedure(proc)

		for stmt in node.body:
			self.visit(stmt)


		self.state.current_procedure.instructions.append(Instruction(InstrSet.halt, [0]))
		self.program.procedures.append(proc)

		self.state.end_procedure()

		

	def visitLiteral(self, node: Node.Literal):
		slot = self.state.get_slot()

		if slot is None:
			raise ValueError()
		
		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.loadi32, [slot, node.value])
		)
		out = Instruction(InstrSet.out, [2, slot])
		self.state.current_procedure.instructions.append(out)
		self.state.push_temp_slot(slot)


	def visitIdentifier(self, node: Node.Identifier):
		pass


	def visitBlock(self, node: Node.Block):
		pass

	def visitIf(self, node: Node.If):
		pass


	def visitWhile(self, node: Node.While):
		pass

	def visitFor(self, node: Node.For):
		pass


	def visitDeclaration(self, node: Node.Declaration):
		self.visit(node.value)
		slot = self.state.pop_temp_slot()
		self.state.set_variable_slot(node.name, slot)
		out = Instruction(InstrSet.out, [2, slot])
		self.state.current_procedure.instructions.append(out)


	def visitAssign(self, node: Node.Assign):
		pass


	def visitBinaryOp(self, node: Node.BinaryOp):
		self.visit(node.left)
		self.visit(node.right)
		slot = self.state.get_slot()

		if slot is None:
			raise ValueError()
		
		t2 = self.state.pop_temp_slot()
		t1 = self.state.pop_temp_slot()

		match node.op:
			case BinaryOpType.Add:
				instr = InstrSet.addi
			case BinaryOpType.Sub:
				instr = InstrSet.subi
			case BinaryOpType.Mul:
				instr = InstrSet.muli
			case BinaryOpType.Div:
				instr = InstrSet.divi

		self.state.current_procedure.instructions.append(
			Instruction(instr, [slot, t1, t2])
		)

		self.state.free_slot(t2)
		self.state.free_slot(t1)

		self.state.push_temp_slot(slot)


	def visitUnaryOp(self, node: Node.UnaryOp):
		pass


	def visitCall(self, node: Node.Call):
		pass