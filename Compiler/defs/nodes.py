from dataclasses import dataclass, field
from typing import List, Optional, Union
from abc import ABC, abstractmethod

from Compiler.defs.op import BinaryOpType, UnaryOpType
from Compiler.defs.expr import ExprLiteralType
from Compiler.defs.node_base import NodeBase
from Compiler.defs.scope import NameScope


class Node:


	@dataclass
	class Program(NodeBase):
		functions: List["Node.Function"]
		n_scope: NameScope = field(default_factory=NameScope)


	@dataclass
	class Function(NodeBase):
		name: str
		params: List["Node.Declaration"]
		body: "Node.Block"
		return_type: Optional[str] = None
		n_scope: NameScope = field(default_factory=NameScope)


	@dataclass
	class Container(NodeBase):
		name: str 
		virtual: bool
		members: list["Node.Declaration"]
		methods: list["Node.Function"] = field(default_factory=list)
		n_scope: NameScope = field(default_factory=NameScope)
		

	class Expression(NodeBase):
		pass


	@dataclass
	class Literal(Expression):
		value: Union[int, float, str, bool]
		type: ExprLiteralType


	@dataclass
	class Identifier(Expression):
		value: str


	@dataclass
	class Block(Expression):
		statements: List["Node.Expression"]
		n_scope: NameScope = field(default_factory=NameScope)


	@dataclass
	class If(Expression):
		condition: "Node.Expression"
		then_branch: "Node.Block"
		else_branch: Optional["Node.Expression"]


	@dataclass
	class While(Expression):
		condition: "Node.Expression"
		body: "Node.Block"


	@dataclass
	class For(Expression):
		init: "Node.Expression"
		condition: "Node.Expression"
		step: "Node.Expression"
		body: "Node.Block"


	@dataclass
	class Declaration(Expression):
		name: str
		type: str
		value: "Node.Expression"


	@dataclass
	class BinaryOp(Expression):
		op: BinaryOpType
		left: "Node.Expression"
		right: "Node.Expression"


	@dataclass
	class UnaryOp(Expression):
		op: UnaryOpType
		operand: "Node.Expression"


	@dataclass
	class Call(Expression):
		callee: "Node.Expression" 
		args: List["Node.Expression"]


	@dataclass
	class Return(Expression):
		value: Optional["Node.Expression"] = None


	@dataclass
	class BuiltinCommand(Expression):
		args: list["Node.Identifier"]





class NodeVisitor(ABC):

	def visit(self, node: NodeBase):
		method_name = f"visit{node.__class__.__name__}"
		visitor_method = getattr(self, method_name, self._generic_visit)
		return visitor_method(node)


	def _generic_visit(self, node: NodeBase):
		raise NotImplementedError(
			f"No visit{node.__class__.__name__} method defined in {self.__class__.__name__}"
		)


	@abstractmethod
	def visitProgram(self, node: Node.Program):
		pass


	@abstractmethod
	def visitFunction(self, node: Node.Function):
		pass


	@abstractmethod
	def visitLiteral(self, node: Node.Literal):
		pass


	@abstractmethod
	def visitIdentifier(self, node: Node.Identifier):
		pass


	@abstractmethod
	def visitBlock(self, node: Node.Block):
		pass


	@abstractmethod
	def visitIf(self, node: Node.If):
		pass


	@abstractmethod
	def visitWhile(self, node: Node.While):
		pass


	@abstractmethod
	def visitFor(self, node: Node.For):
		pass


	@abstractmethod
	def visitDeclaration(self, node: Node.Declaration):
		pass


	@abstractmethod
	def visitBinaryOp(self, node: Node.BinaryOp):
		pass


	@abstractmethod
	def visitUnaryOp(self, node: Node.UnaryOp):
		pass


	@abstractmethod
	def visitCall(self, node: Node.Call):
		pass


	@abstractmethod
	def visitReturn(self, node: Node.Return):
		pass

	@abstractmethod
	def visitBuiltinCommand(self, node: Node.BuiltinCommand):
		pass

	@abstractmethod
	def visitContainer(self, node: Node.Container):
		pass