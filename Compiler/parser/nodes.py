from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Union


class BinaryOpType(Enum):
	Add = auto()
	Sub = auto()
	Mul = auto()
	Div = auto()
	Mod = auto()
	Pow = auto()
	Eq = auto()
	Neq = auto()
	Lt = auto()
	Gt = auto()
	Lte = auto()
	Gte = auto()
	And = auto()
	Or = auto()
	BitAnd = auto()
	BitOr = auto()
	BitXor = auto()
	Shl = auto()
	Shr = auto()


class UnaryOpType(Enum):
	Negate = auto()
	Not = auto()
	BitNot = auto()


class Node:


	class Base:
		pass


	@dataclass
	class Program(Base):
		statements: List["Node.Base"] = field(default_factory=list)


	@dataclass
	class Function(Base):
		name: str
		params: List[str]
		body: List["Node.Base"]
		return_type: Optional[str] = None


	class Expression(Base):
		pass


	@dataclass
	class Literal(Expression):
		value: Union[int, float, str, bool]


	@dataclass
	class Identifier(Expression):
		name: str


	@dataclass
	class Block(Expression):
		statements: List["Node.Expression"]


	@dataclass
	class If(Expression):
		condition: "Node.Expression"
		then_branch: "Node.Expression"
		else_branch: Optional["Node.Expression"]


	@dataclass
	class While(Expression):
		condition: "Node.Expression"
		body: "Node.Block"


	@dataclass
	class For(Expression):
		init: "Node.Expression"
		condition: "Node.Expression"
		end: "Node.Expression"
		body: "Node.Block"


	@dataclass
	class Declaration(Expression):
		name: str
		type: str
		value: "Node.Expression"

		
	@dataclass
	class Assign(Expression):
		name: str
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
		name: str
		args: List["Node.Expression"]