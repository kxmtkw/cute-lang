from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.defs.scope import NameScope



class Resolver(NodeVisitor):


	def __init__(self) -> None:
		super().__init__()
		self.current_scope: NameScope


	def descend_scope(self, scope: NameScope):
		scope.parent = self.current_scope
		self.current_scope = scope


	def ascend_scope(self):
		self.current_scope = self.current_scope.parent


	def visitProgram(self, node: Node.Program):
		self.current_scope = node.n_scope
		self.current_scope["__builtin__"] = Node.Function("", [], Node.Block([]))

		for func in node.functions:
			self.visit(func)


	def visitFunction(self, node: Node.Function):

		if self.current_scope.has(node.name):
			raise ValueError(f"Redefinition of function: {node.name}")
		
		self.current_scope[node.name] = node

		self.descend_scope(node.n_scope)

		for decl in node.params:
			self.visit(decl)

		self.visit(node.body)

		self.ascend_scope()


	def visitLiteral(self, node: Node.Literal):
		pass


	def visitIdentifier(self, node: Node.Identifier):
		found_node = self.current_scope.get(node.value, None)
		if found_node is None:
			raise ValueError(f"Unknown identifier: {node.value}")


	def visitBlock(self, node: Node.Block):
		self.descend_scope(node.n_scope)

		for stmt in node.statements:
			self.visit(stmt)

		self.ascend_scope()


	def visitIf(self, node: Node.If):
		self.visit(node.condition)
		self.visit(node.then_branch)
		if node.else_branch:
			self.visit(node.else_branch)


	def visitWhile(self, node: Node.While):
		self.visit(node.condition)
		self.visit(node.body)


	def visitFor(self, node: Node.For):
		self.visit(node.init)
		self.visit(node.condition)
		self.visit(node.step)
		self.visit(node.body)


	def visitDeclaration(self, node: Node.Declaration):

		if self.current_scope.has(node.name):
			raise ValueError(f"Identifier already defined within scope: {node.name}")

		# found_type_node = self.current_scope.get(node.type, None)
		# if found_type_node is None:
		# 	raise ValueError(f"Unknown identifier: {node.type}")

		self.current_scope[node.name] = node

		if node.value is not None:
			self.visit(node.value)


	def visitBinaryOp(self, node: Node.BinaryOp):
		self.visit(node.left)
		self.visit(node.right)


	def visitUnaryOp(self, node: Node.UnaryOp):
		self.visit(node.operand)


	def visitCall(self, node: Node.Call):
		self.visit(node.callee)
		for arg in node.args:
			self.visit(arg)


	def visitReturn(self, node: Node.Return):
		if node.value is not None:
			self.visit(node.value)


	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		pass

	
	def visitContainer(self, node: Node.Container):
		self.current_scope[node.name] = node

		for member in node.members:
			node.n_scope[member.name] = member