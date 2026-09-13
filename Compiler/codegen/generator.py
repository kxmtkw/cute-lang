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


	def assignProcedureId(self, func: Node.Function):
		if func.name == "main":
			proc_id = 0
		else:
			proc_id = self.state.get_procedure_id()

		func.c_proc_id = proc_id

	
	def visitProgram(self, node: Node.Program):

		for func in node.functions:
			self.visit(func)

		self.program.assemble(self.builder)
		image = self.builder.compile()

		with open(self.outpath, "wb") as file:
			file.write(image)

		print(self.program)
		return node


	def visitFunction(self, node: Node.Function):

		self.assignProcedureId(node)

		assert node.c_proc_id is not None

		proc = Procedure(node.c_proc_id, len(node.params), [])

		self.state.new_procedure(proc)

		for param in node.params:
			self.visit(param)

		self.visit(node.body)

		self.program.procedures.append(proc)

		self.state.end_procedure()

		return node

		

	def visitLiteral(self, node: Node.Literal):
		slot = self.state.get_tmp_slot()

		value: int | float

		if slot is None:
			raise ValueError()

		match node.type:
			case ExprLiteralType.Int:
				instr = InstrSet.loadi32
				value = int(node.value)
			case ExprLiteralType.Float:
				instr = InstrSet.loadf32
				value = float(node.value)
			case ExprLiteralType.Bool:
				instr = InstrSet.loadbyte
				value = 1 if node.value else 0
			case ExprLiteralType.Char:
				instr = InstrSet.loadbyte
				value = ord(str(node.value))
			case ExprLiteralType.String:
				raise ValueError("String literals are not supported yet.")

		self.state.current_procedure.instructions.append(
			Instruction(instr, [slot, value])
		)
		
		self.state.push_slot(slot)
		return node


	def visitIdentifier(self, node: Node.Identifier):

		referred_node = node.n_refers
		assert referred_node is not None

		if isinstance(referred_node, Node.Declaration):
			assert referred_node.c_slot_id is not None
			self.state.push_slot(referred_node.c_slot_id)

		elif isinstance(referred_node, Node.Function):
			if referred_node.c_proc_id is None:
				self.assignProcedureId(referred_node)

			assert referred_node.c_proc_id is not None

			slot = self.state.get_tmp_slot()

			assert slot is not None

			self.state.current_procedure.instructions.append(
				Instruction(InstrSet.loadu32, [slot, referred_node.c_proc_id])
			)

			self.state.push_slot(slot)

		else:
			raise ValueError(f"Identifier refers to {node.n_refers} which cannot be converted into any bytecode representative.")

		return node
	

	def visitBlock(self, node: Node.Block):
		for stmt in node.statements:
			self.visit(stmt)
		return node


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

		return node


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

		return node

		

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

		return node


	def visitDeclaration(self, node: Node.Declaration):

		slot = self.state.get_slot()
		assert slot is not None

		node.c_slot_id = slot

		if node.value is not None:
			self.visit(node.value)
		
			value_slot = self.state.pop_slot()

			self.state.current_procedure.instructions.append(
				Instruction(InstrSet.mov, [slot, value_slot])
			)
			self.state.free_slot_if_tmp(value_slot)

		return node


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
			assert slot is not None
			instr = INSTRUCTION_ENCODING_TABLE[node.op]
			operation = Instruction(instr, [slot, t1, t2])
			self.state.current_procedure.instructions.append(operation)
			self.state.push_slot(slot)

		elif node.op in CMP_INSTRUCTION_ENCODING_TABLE:
			slot = self.state.get_tmp_slot()
			assert slot is not None
			instr = CMP_INSTRUCTION_ENCODING_TABLE[node.op]
			self.state.current_procedure.instructions.append(Instruction(InstrSet.cmpi, [t1, t2]))
			self.state.current_procedure.instructions.append(Instruction(instr, [slot]))
			self.state.push_slot(slot)
	

		self.state.free_slot_if_tmp(t2)
		self.state.free_slot_if_tmp(t1)

		return node
		

	def visitUnaryOp(self, node: Node.UnaryOp):
		return node


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

		return node


	def visitCall(self, node: Node.Call):

		slots = self.state.get_continous_slots(len(node.args))

		if len(node.args) > 0:

			assert slots is not None

			for i, arg in enumerate(node.args):
				self.visit(arg)
				expr_slot = self.state.pop_slot()
				mov = Instruction(InstrSet.mov, [slots[i], expr_slot])
				self.state.current_procedure.instructions.append(mov)
				self.state.free_slot_if_tmp(expr_slot)

		self.visit(node.callee)

		callee_slot = self.state.pop_slot()
		return_slot = self.state.get_tmp_slot()

		assert return_slot is not None
		arg_start_slot = slots[0] if slots is not None else 0

		self.state.current_procedure.instructions.append(
			Instruction(InstrSet.call, [callee_slot, arg_start_slot, return_slot])
		)

		self.state.push_slot(return_slot)
		self.state.free_slot_if_tmp(callee_slot)

		if slots is not None:
			for slot in slots:
				self.state.free_slot_if_tmp(slot)

		return node


	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		self.builtin.handle(node)
		return node


	def visitContainer(self, node: Node.Container):
		return super().visitContainer(node)