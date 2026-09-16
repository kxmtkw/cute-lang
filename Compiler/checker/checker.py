from typing import Optional

from Compiler.defs.expr import ExprLiteralType
from Compiler.defs.node_base import NodeBase
from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.defs.op import BinaryOpType
from Compiler.defs.scope import NameScope



class Checker(NodeVisitor):


	def __init__(self) -> None:
		super().__init__()
		self.current_function_return_type: Optional[Node.Container]
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

		for artif in node.artifacts:
			self.visit(artif)

		return node


	def visitFunction(self, node: Node.Function):
		
		self.descend_scope(node.n_scope)

		for decl in node.params:
			self.visit(decl)

		assert node.return_type
		self.visit(node.return_type)

		self.current_function_return_type = node.return_type.t_type

		self.visit(node.body)

		self.ascend_scope()

		return node


	def visitLiteral(self, node: Node.Literal):
		if node.literal_type == ExprLiteralType.Int:
			node.t_type = self.current_scope.get("int", None)
		elif node.literal_type == ExprLiteralType.Float:
			node.t_type = self.current_scope.get("float", None)
		return node


	def visitIdentifier(self, node: Node.Identifier):

		assert node.n_refers

		if isinstance(node.n_refers, Node.Declaration):
			assert node.n_refers.type
			node.t_type = node.n_refers.type.t_type

		elif isinstance(node.n_refers, Node.Container):
			node.t_type = node.n_refers

		elif isinstance(node.n_refers, Node.Function):
			node.t_type = node.n_refers.return_type.t_type

		else:
			raise ValueError(f"Identifier {node.value} refers to unsupported thing {node.n_refers}")

		
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

		assert node.type
		self.visit(node.type)

		assert node.type.t_type

		if node.value is not None:
			self.visit(node.value)

			if node.type.t_type is not node.value.t_type:
				raise TypeError(f"Expected {node.type.t_type.name}, got {node.value.t_type.name}")

		return node


	def visitBinaryOp(self, node: Node.BinaryOp):
		self.visit(node.left)
		self.visit(node.right)

		if node.left.t_type is not node.right.t_type:
			raise ValueError()

		node.t_type = node.left.t_type
		
		return node


	def visitUnaryOp(self, node: Node.UnaryOp):
		self.visit(node.operand)
		return node


	def visitCall(self, node: Node.Call):
		self.visit(node.callee)

		for arg in node.args:
			self.visit(arg)

		node.t_type = node.callee.t_type
		return node


	def visitReturn(self, node: Node.Return):
		if node.value is not None:
			self.visit(node.value)
			if self.current_function_return_type is not node.value.t_type:
				raise ValueError("Function returns the wrong type.")
		return node


	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		return node

	
	def visitContainer(self, node: Node.Container):

		if node.virtual:
			return node

		for field in node.fields:
			self.visit(field)

		return node


	def visitContainerImpl(self, node: Node.ContainerImpl):

		assert node.n_refers

		for method in node.methods:
			self.visit(method)
			node.n_refers.methods.append(method)

			if method.name == "__new__":
				assert method.return_type.t_type is node.n_refers
				continue

			identifier = Node.Identifier(node.n_refers.name)
			identifier.n_refers = node.n_refers
			method.params.insert(0, Node.Declaration("this", identifier, value=None))
			

		return node