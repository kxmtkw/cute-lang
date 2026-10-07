from enum import Enum, auto


class BinaryOpType(Enum):
	Access = auto()
	Assign = auto()
	Add = auto()
	Sub = auto()
	Mul = auto()
	Div = auto()
	Mod = auto()
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
