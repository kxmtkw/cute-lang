from typing import Literal, Optional

from Compiler.defs.node_base import NodeBase
from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.defs.op import BinaryOpType
from Compiler.defs import var
import Compiler.defs.symbols as sym



class TypeChecker(NodeVisitor):


	def __init__(self) -> None:
		super().__init__()
		self.program: Node.Program
		self.current_symtable: sym.SymbolTable

		self.symbol_stack: list[sym.Symbol] = []

		self.current_func_sym: sym.Function


	def typeof(self, symbol: sym.Symbol) -> sym.Container:
		"Returns the 'type' of any symbol."
		if isinstance(symbol, sym.Function):
			return symbol.returns
		elif isinstance(symbol, sym.Variable):
			return symbol.type
		elif isinstance(symbol, sym.Container):
			return symbol

		return None


	def visitProgram(self, node: Node.Program):

		self.program = node
		self.current_symtable = node.symtable

		self.first_pass = True

		for artif in node.artifacts:
			self.visit(artif)

		return node


	def visitFunction(self, node: Node.Function):

		self.current_symtable = node.symtable.set_parent(self.current_symtable)

		self.current_func_sym = node.symbol

		for decl in node.params:
			self.visit(decl)

		self.visit(node.return_type)

		self.current_func_sym.returns = self.symbol_stack.pop()
		assert isinstance(self.current_func_sym.returns, sym.Container)
		
		self.visit(node.body)

		self.current_symtable = self.current_symtable.get_parent()

		return node


	def visitLiteral(self, node: Node.Literal):
		match node.type:
			case "int":
				self.symbol_stack.append(self.current_symtable.recursive_get("int"))
			case "float":
				self.symbol_stack.append(self.current_symtable.recursive_get("float"))
			case "bool":
				self.symbol_stack.append(self.current_symtable.recursive_get("bool"))
		return node


	def visitIdentifier(self, node: Node.Identifier):
		symbol =  self.current_symtable.recursive_get(node.value)
		assert symbol
		self.symbol_stack.append(symbol)
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
		self.current_symtable = node.symtable.set_parent(self.current_symtable)
		self.visit(node.init)
		self.visit(node.condition)
		self.visit(node.step)
		self.visit(node.body)
		self.current_symtable = node.symtable.get_parent()
		return node
		

	def visitDeclaration(self, node: Node.Declaration):

		if node.type is not None:
			self.visit(node.type)

		assert node.symbol
		type_sym = self.symbol_stack.pop()

		if not isinstance(type_sym, sym.Container):
			raise ValueError(f"Expected type to be a container, not {type_sym}.")

		node.symbol.type = type_sym

		if node.value is not None:
			self.visit(node.value)

			value_sym = self.symbol_stack.pop()
			value_type_sym = self.typeof(value_sym)

			if value_type_sym is None:
				raise ValueError(f"{value_sym} is not assignable to {node.symbol}")

			if value_type_sym is not node.symbol.type:
				raise ValueError(f"{value_type_sym} is not assignable to {node.symbol}")
			
		return node


	def visitBinaryOp(self, node: Node.BinaryOp):
		self.visit(node.left)
		self.visit(node.right)

		typer = self.typeof(self.symbol_stack.pop())
		typel = self.typeof(self.symbol_stack.pop())

		if typer is not typel:
			raise ValueError(f"Cannot perform {node.op} between {node.left} and {node.right}.")

		self.symbol_stack.append(typer)

		return node


	def visitUnaryOp(self, node: Node.UnaryOp):
		self.visit(node.operand)
		return node


	def visitCall(self, node: Node.Call):
		self.visit(node.callee)

		func_sym = self.symbol_stack.pop()

		if not isinstance(func_sym, sym.Function):
			raise ValueError()

		type_sym = func_sym.returns

		self.symbol_stack.append(type_sym)

		for arg in node.args:
			self.visit(arg)

		return node


	def visitReturn(self, node: Node.Return):
		if node.value is not None:
			self.visit(node.value)

		type_sym = self.typeof(self.symbol_stack.pop())

		if type_sym is not self.current_func_sym.returns:
			raise ValueError()
		
		return node


	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		return node

	
	def visitContainer(self, node: Node.Container):

		assert node.symbol

		for member in node.fields:
			self.visit(member)
		
		return node


	def visitContainerImpl(self, node: Node.ContainerImpl):

		if node.name not in self.current_symtable:
			raise ValueError("Container not found so can not be implemented")
		
		container = self.current_symtable[node.name]
		assert isinstance(container, sym.Container)
		node.symbol = container

		for method in node.methods:
			self.visit(method)

		return node