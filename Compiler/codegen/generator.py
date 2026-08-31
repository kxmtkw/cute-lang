from Compiler.codegen.state import GeneratorState
from Compiler.parser.nodes import BinaryOpType, NodeVisitor, Node
from Compiler.codegen.image import ImageBuilder
from Compiler.codegen.program import Program, Procedure, Label, Constant, Instruction, InstrSet
from Compiler.codegen.builtin import BuiltinHandler



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



class CodeGenerator(NodeVisitor):

	def __init__(self) -> None:
		super().__init__()
		self.state = GeneratorState()
		self.builder = ImageBuilder()
		self.program = Program([], [])
		self.builtin = BuiltinHandler(self.state, self.builder, self.program)

	
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

		slot = self.state.get_slot()
		self.state.set_variable_slot(node.name, slot)
		
		if node.value is not None:
			self.visit(node.value)
		
			value_slot = self.state.pop_slot()

			self.state.current_procedure.instructions.append(
				Instruction(InstrSet.mov, [slot, value_slot])
			)
			self.state.free_slot_if_tmp(value_slot)



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


		if isinstance(node.callee, Node.Identifier):
			if node.callee.name == "__builtin__":
				self.builtin.handle(node)
				return

		# slots = self.state.get_continous_slots(len(node.args))

		# for i, arg in enumerate(node.args):
		# 	self.visit(arg)
		# 	expr_slot = self.state.pop_slot()
		# 	mov = Instruction(InstrSet.mov, [slots[i], expr_slot])

		
