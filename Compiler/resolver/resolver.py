from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.defs.scope import NameScope



class Resolver(NodeVisitor):


	def __init__(self) -> None:
		super().__init__()
		self.in_builtin_context: bool = False
		self.current_scope: NameScope


	def descend_scope(self, scope: NameScope):
		scope.parent = self.current_scope
		self.current_scope = scope


	def ascend_scope(self):
		if self.current_scope.parent is None:
			raise ValueError("No parent scope to ascend to.")
		
		self.current_scope = self.current_scope.parent


	def visitProgram(self, node: Node.Program):
		self.current_scope = node.n_scope

		for func in node.functions:
			self.visit(func)

		return node


	def visitFunction(self, node: Node.Function):

		if self.current_scope.has(node.name):
			raise ValueError(f"Redefinition of function: {node.name}")
		
		self.current_scope[node.name] = node

		self.descend_scope(node.n_scope)

		for decl in node.params:
			self.visit(decl)

		self.visit(node.body)

		self.ascend_scope()

		return node


	def visitLiteral(self, node: Node.Literal):
		return node


	def visitIdentifier(self, node: Node.Identifier):
		found_node = self.current_scope.get(node.value, None)
		if found_node is None and not self.in_builtin_context:
			raise ValueError(f"Unknown identifier: {node.value}")
		node.n_refers = found_node
		return node


	def visitBlock(self, node: Node.Block):
		self.descend_scope(node.n_scope)

		for stmt in node.statements:
			self.visit(stmt)

		self.ascend_scope()
		return node


	def visitIf(self, node: Node.If):
		self.visit(node.condition)
		self.visit(node.then_branch)
		if node.else_branch:
			self.visit(node.else_branch)
		return node


	def visitWhile(self, node: Node.While):
		self.visit(node.condition)
		self.visit(node.body)
		return node


	def visitFor(self, node: Node.For):
		self.visit(node.init)
		self.visit(node.condition)
		self.visit(node.step)
		self.visit(node.body)
		return node
		

	def visitDeclaration(self, node: Node.Declaration):

		if self.current_scope.has(node.name):
			raise ValueError(f"Identifier already defined within scope: {node.name}")

		# found_type_node = self.current_scope.get(node.type, None)
		# if found_type_node is None:
		# 	raise ValueError(f"Unknown identifier: {node.type}")

		self.current_scope[node.name] = node

		if node.value is not None:
			self.visit(node.value)

		return node


	def visitBinaryOp(self, node: Node.BinaryOp):
		self.visit(node.left)
		self.visit(node.right)
		return node


	def visitUnaryOp(self, node: Node.UnaryOp):
		self.visit(node.operand)
		return node


	def visitCall(self, node: Node.Call):
		self.visit(node.callee)
		for arg in node.args:
			self.visit(arg)

		return node


	def visitReturn(self, node: Node.Return):
		if node.value is not None:
			self.visit(node.value)
		return node


	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		# fix for now, we want the builtin handler to handle errors 
		self.in_builtin_context = True
		for arg in node.args:
			self.visit(arg)
		self.in_builtin_context = False
		return node

	
	def visitContainer(self, node: Node.Container):
		self.current_scope[node.name] = node

		for member in node.fields:
			node.n_scope[member.name] = member

		return node