from dataclasses import dataclass, field
from enum import Enum
from typing import List, Literal, Optional, Union
from abc import ABC, abstractmethod

from Compiler.defs.op import BinaryOpType, UnaryOpType
from Compiler.defs.expr import ExprLiteralType



class Node:

	class Base:

		def dump(self, level: int = 0) -> str:
			indent = "  " * level
			node_name = self.__class__.__name__

			children: List[tuple[str, Union["Node.Base", List["Node.Base"]]]] = []
			info_bits = []

			for k, v in self.__dict__.items():
				if isinstance(v, Node.Base) or (
					isinstance(v, list) and v and isinstance(v[0], Node.Base)
				):
					children.append((k, v))
				elif isinstance(v, Enum):
					info_bits.append(f"{k}={v.name}")
				elif v is not None:
					info_bits.append(f"{k}={v!r}")

			info_str = f" ({', '.join(info_bits)})" if info_bits else ""
			lines = [f"{indent}{node_name}{info_str}"]

			for name, child in children:
				if isinstance(child, list):
					lines.append(f"{indent}  {name}:")
					for item in child:
						lines.append(item.dump(level + 2))
				else:
					lines.append(f"{indent}  {name}:")
					lines.append(child.dump(level + 2))

			return "\n".join(lines)

		def __repr__(self) -> str:
			return self.dump()


	@dataclass
	class Program(Base):
		functions: List["Node.Function"]


	@dataclass
	class Function(Base):
		name: str
		params: List["Node.Declaration"]
		body: "Node.Block"
		return_type: Optional[str] = None


	class Expression(Base):
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


	@dataclass
	class If(Expression):
		condition: "Node.Expression"
		then_branch: "Node.Block"
		else_branch: Optional["Node.Block"]


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



class NodeVisitor(ABC):

	def visit(self, node: Node.Base):
		method_name = f"visit{node.__class__.__name__}"
		visitor_method = getattr(self, method_name, self._generic_visit)
		return visitor_method(node)


	def _generic_visit(self, node: Node.Base):
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