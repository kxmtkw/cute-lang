from Compiler.codegen.state import GeneratorState
from Compiler.defs.expr import ExprLiteralType
from Compiler.defs.op import BinaryOpType, UnaryOpType
from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.imagen.image import ImageBuilder
from Compiler.imagen.program import Program, Procedure, Label, Constant, Instruction, InstrSet
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
	BinaryOpType.Shr: InstrSet.bshr
}

CMP_INSTRUCTION_ENCODING_TABLE: dict[BinaryOpType, InstrSet] = {
	BinaryOpType.Eq: InstrSet.eq,
	BinaryOpType.Neq: InstrSet.ne,
	BinaryOpType.Lt: InstrSet.lt,
	BinaryOpType.Lte: InstrSet.le,
	BinaryOpType.Gt: InstrSet.gt,
	BinaryOpType.Gte: InstrSet.ge,
}


class CodeGenerator(NodeVisitor):

	def __init__(self, outpath: str) -> None:
		super().__init__()
		self.outpath = outpath
		self.state = GeneratorState()
		self.builder = ImageBuilder()
		self.program = Program([], [])
		self.builtin = BuiltinHandler(self.state, self.builder, self.program)

	
	def visitProgram(self, node: Node.Program):
		for func in node.functions:
			self.visit(func)

		self.program.assemble(self.builder)
		image = self.builder.compile()
		with open(self.outpath, "wb") as file:
			file.write(image)

		print(self.program)


	def visitFunction(self, node: Node.Function):
		proc = Procedure(self.state.get_procedure_id(node.name), len(node.params), [])

		self.state.new_procedure(proc)

		for param in node.params:
			self.visit(param)

		self.visit(node.body)

		self.program.procedures.append(proc)

		self.state.end_procedure()

		

	def visitLiteral(self, node: Node.Literal):
		slot = self.state.get_tmp_slot()

		if slot is None:
			raise ValueError()

		match node.type:
			case ExprLiteralType.Int:
				instr = InstrSet.loadi32
			case ExprLiteralType.Float:
				instr = InstrSet.loadf32
			case ExprLiteralType.Bool:
				instr = InstrSet.loadbyte
				node.value = 1 if node.value else 0
			case ExprLiteralType.Char:
				instr = InstrSet.loadbyte
				node.value = ord(node.value)
			case ExprLiteralType.String:
				raise ValueError("String literals are not supported yet.")

		self.state.current_procedure.instructions.append(
			Instruction(instr, [slot, node.value])
		)
		
		self.state.push_slot(slot)


	def visitIdentifier(self, node: Node.Identifier):
		slot = self.state.get_variable_slot(node.value)
		if slot is None:
			slot = self.state.get_tmp_slot()
			id = self.state.get_procedure_id(node.value)
			self.state.current_procedure.instructions.append(
				Instruction(InstrSet.loadu32, [slot, id])
			)
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

		loop_start = Label(self.state.label())
		loop_end = Label(self.state.label())
		self.visit(node.init)
		self.state.current_procedure.instructions.append(loop_start)
		self.visit(node.condition)
		t1 = self.state.pop_slot()
		self.state.free_slot_if_tmp(t1)
		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.jmpifn, [t1, loop_end])
		)
		self.visit(node.body)
		self.visit(node.step)
		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.jmp, [loop_start])
		)
		self.state.current_procedure.instructions.append(loop_end)


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

		elif node.op in CMP_INSTRUCTION_ENCODING_TABLE:
			slot = self.state.get_tmp_slot()
			instr = CMP_INSTRUCTION_ENCODING_TABLE[node.op]
			self.state.current_procedure.instructions.append(Instruction(InstrSet.cmpi, [t1, t2]))
			self.state.current_procedure.instructions.append(Instruction(instr, [slot]))
			self.state.push_slot(slot)
	

		self.state.free_slot_if_tmp(t2)
		self.state.free_slot_if_tmp(t1)
		

	def visitUnaryOp(self, node: Node.UnaryOp):
		pass


	def visitReturn(self, node: Node.Return):
		if node.value is not None:
			self.visit(node.value)
			slot = self.state.pop_slot()
			self.state.free_slot_if_tmp(slot)
			self.state.current_procedure.instructions.append(
				Instruction(InstrSet.retval, [slot])
			)
		else:
			self.state.current_procedure.instructions.append(
				Instruction(InstrSet.ret, [])
			)


	def visitCall(self, node: Node.Call):

		slots = self.state.get_continous_slots(len(node.args))

		for i, arg in enumerate(node.args):
			self.visit(arg)
			expr_slot = self.state.pop_slot()
			mov = Instruction(InstrSet.mov, [slots[i], expr_slot])
			self.state.current_procedure.instructions.append(mov)
			self.state.free_slot_if_tmp(expr_slot)

		self.visit(node.callee)
		callee_slot = self.state.pop_slot()
		return_slot = self.state.get_tmp_slot()
		arg_start_slot = slots[0]

		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.call, [callee_slot, arg_start_slot, return_slot])
		)

		self.state.push_slot(return_slot)
		self.state.free_slot_if_tmp(callee_slot)
		for slot in slots:
				self.state.free_slot_if_tmp(slot)


	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		self.builtin.handle(node)

	def visitContainer(self, node: Node.Container):
		return super().visitContainer(node)