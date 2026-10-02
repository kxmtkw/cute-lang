from typing import Optional

from Compiler.defs.node_base import NodeBase
from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.defs.op import BinaryOpType
import Compiler.defs.symbols as sym



class Resolver(NodeVisitor):


	def __init__(self) -> None:
		super().__init__()
		self.in_builtin_context: bool = False
		self.callee_context: bool = False
		self.current_symtable: sym.SymbolTable


	def visitProgram(self, node: Node.Program):
		self.current_symtable = node.symtable

		for artif in node.artifacts:
			self.visit(artif)

		return node


	def visitFunction(self, node: Node.Function):

		if node.name in self.current_symtable:
			raise ValueError(f"Redefinition of function: {node.name}")

		node.symbol = sym.Function()
		node.symbol.name = node.name

		self.current_symtable[node.name] = node.symbol

		self.current_symtable = node.symtable.set_parent(self.current_symtable)

		for decl in node.params:
			self.visit(decl)

		self.visit(node.return_type)
		self.visit(node.body)

		self.current_symtable = self.current_symtable.get_parent()

		return node


	def visitLiteral(self, node: Node.Literal):
		return node


	def visitIdentifier(self, node: Node.Identifier):
		symbol = self.current_symtable.recursive_get(node.value, default=None)
		if symbol is None and not self.in_builtin_context:
			raise ValueError(f"Unknown identifier: {node.value}")
		node.refers = symbol
		return node


	def visitBlock(self, node: Node.Block):

		self.current_symtable = node.symtable.set_parent(self.current_symtable)

		for stmt in node.statements:
			self.visit(stmt)

		self.current_symtable = self.current_symtable.get_parent()

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

		if node.name in self.current_symtable:
			raise ValueError(f"Identifier already defined within scope: {node.name}")
		
		if node.type is not None:
			self.visit(node.type)

		node.symbol = sym.Variable()
		node.symbol.name = node.name

		self.current_symtable[node.name] = node.symbol

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

		node.symbol = sym.Container()
		node.symbol.name = node.name
		node.symbol.virtual = node.virtual

		self.current_symtable[node.symbol.name] = node.symbol

		for member in node.fields:
			self.visit(member)
			assert member.symbol
			node.symbol.fields[member.symbol.name] = member.symbol

		
		return node


	def visitContainerImpl(self, node: Node.ContainerImpl):

		if node.name not in self.current_symtable:
			raise ValueError("Container not found so can not be implemented")
		
		container = self.current_symtable[node.name]
		assert isinstance(container, sym.Container)
		node.symbol = container

		for method in node.methods:
			# we also need to make sure here that any method name is not a field name
			self.visit(method)
			assert method.symbol
			container.methods[method.symbol.name] = method.symbol

		return node