from Compiler.parser.nodes import BinaryOpType, NodeVisitor, Node
from Compiler.codegen.image import ImageBuilder
from Compiler.codegen.program import Program, Procedure, Label, Constant, Instruction, InstrSet


SLOT_COUNT = 256


INSTRUCTION_ENCODING_TABLE: dict[BinaryOpType, InstrSet] = {
	BinaryOpType.Add: InstrSet.addi,
	BinaryOpType.Sub: InstrSet.subi,
	BinaryOpType.Mul: InstrSet.muli,
	BinaryOpType.Div: InstrSet.divi,
	BinaryOpType.Mod: InstrSet.modi,
	BinaryOpType.And: InstrSet.and_,
	BinaryOpType.Or: InstrSet.or_,
	BinaryOpType.BitAnd: InstrSet.band,
	BinaryOpType.BitOr: InstrSet.bor,
	BinaryOpType.BitXor: InstrSet.bxor,
	BinaryOpType.Shl: InstrSet.bshl,
	BinaryOpType.Shr: InstrSet.bshr,
}

class GeneratorState:


	def __init__(self) -> None:
		self._current_procedure: Procedure | None = None
		self._proc_slots: list[bool] = []
		self._tmp_slots: set[int] = set()
		self._slots_stack: list[int] = []
		self._variable_assignments: dict[str, int] = {} # variable name to slot
		self._label_num: int = 0


	def new_procedure(self, proc: Procedure):
		if self._current_procedure is not None:
			raise ValueError()
		self._current_procedure = proc
		self._proc_slots = [False for slot in range(SLOT_COUNT)]
		self._tmp_slots: set[int] = set()
		self._slots_stack.clear()
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


	def get_tmp_slot(self) -> int | None:
		for i, slot in enumerate(self._proc_slots):
			if not slot:
				self._proc_slots[i] = True
				self._tmp_slots.add(i)
				return i
		return None
	

	def free_slot(self, slot: int):
		self._proc_slots[slot] = False
		if slot in self._tmp_slots: self._tmp_slots.remove(slot)


	def free_slot_if_tmp(self, slot: int):
		if slot in self._tmp_slots:
			self._proc_slots[slot] = False
			self._tmp_slots.remove(slot)


	def push_slot(self, slot: int):
		self._slots_stack.append(slot)


	def pop_slot(self) -> int:
		return self._slots_stack.pop()


	def set_variable_slot(self, name: str, slot: int):
		self._variable_assignments[name] = slot


	def get_variable_slot(self, name: str) -> int:
		return self._variable_assignments[name]


	def label(self) -> int:
		self._label_num += 1
		return self._label_num




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

		print(self.program)


	def visitFunction(self, node: Node.Function):
		proc = Procedure(0, 0, [])

		self.state.new_procedure(proc)

		for stmt in node.body:
			self.visit(stmt)


		self.state.current_procedure.instructions.append(Instruction(InstrSet.halt, [0]))
		self.program.procedures.append(proc)

		self.state.end_procedure()

		

	def visitLiteral(self, node: Node.Literal):
		slot = self.state.get_tmp_slot()

		if slot is None:
			raise ValueError()
		
		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.loadi32, [slot, node.value])
		)
		self.state.push_slot(slot)


	def visitIdentifier(self, node: Node.Identifier):
		slot = self.state.get_variable_slot(node.name)
		self.state.push_slot(slot)


	def visitBlock(self, node: Node.Block):

		for stmt in node.statements:
			self.visit(stmt)


	def visitIf(self, node: Node.If):

		end_if_label = Label(self.state.label())
		else_branch_label = Label(self.state.label())

		self.visit(node.condition)
		condition_slot = self.state.pop_slot()
		self.state.free_slot_if_tmp(condition_slot)

		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.jmpifn, [condition_slot, else_branch_label if node.else_branch else end_if_label])
		)
		self.visit(node.then_branch)
		
		if node.else_branch:
			self.state.current_procedure.instructions.append(Instruction(InstrSet.jmp, [end_if_label]))
			self.state.current_procedure.instructions.append(else_branch_label)
			self.visit(node.else_branch)

		self.state.current_procedure.instructions.append(end_if_label)


	def visitWhile(self, node: Node.While):

		loop_start = Label(self.state.label())
		loop_end = Label(self.state.label())
		self.state.current_procedure.instructions.append(loop_start)

		self.visit(node.condition)
		t1 = self.state.pop_slot()
		self.state.free_slot_if_tmp(t1)
		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.jmpifn, [t1, loop_end])
		)
		self.visit(node.body)
		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.jmp, [loop_start])
		)
		self.state.current_procedure.instructions.append(loop_end)

		

	def visitFor(self, node: Node.For):
		pass


	def visitDeclaration(self, node: Node.Declaration):
		self.visit(node.value)
		slot = self.state.get_slot()
		self.state.set_variable_slot(node.name, slot)

		value_slot = self.state.pop_slot()

		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.mov, [slot, value_slot])
		)

		self.state.free_slot_if_tmp(value_slot)

		out = Instruction(InstrSet.out, [2, slot])
		self.state.current_procedure.instructions.append(out)


	def visitAssign(self, node: Node.Assign):
		pass


	def visitBinaryOp(self, node: Node.BinaryOp):
		self.visit(node.left)
		self.visit(node.right)

		
		t2 = self.state.pop_slot()
		t1 = self.state.pop_slot()

		if node.op == BinaryOpType.Assign:
			mov = Instruction(InstrSet.mov, [t1, t2])
			self.state.current_procedure.instructions.append(mov)
			out = Instruction(InstrSet.out, [2, t1])
			self.state.current_procedure.instructions.append(out)

		elif node.op in INSTRUCTION_ENCODING_TABLE:
			slot = self.state.get_tmp_slot()
			instr = INSTRUCTION_ENCODING_TABLE[node.op]
			operation = Instruction(instr, [slot, t1, t2])
			self.state.current_procedure.instructions.append(operation)
			self.state.push_slot(slot)
	

		self.state.free_slot_if_tmp(t2)
		self.state.free_slot_if_tmp(t1)
		

	def visitUnaryOp(self, node: Node.UnaryOp):
		pass


	def visitCall(self, node: Node.Call):
		pass
