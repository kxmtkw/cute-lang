from typing import Union

from Compiler.parser.nodes import Node, BinaryOpType, UnaryOpType


OPERATOR_PRECEDENCE: dict[Union[UnaryOpType, BinaryOpType], int] = {

	# higheset precedence

	UnaryOpType.Negate: 0,
	UnaryOpType.Not: 0,
	UnaryOpType.BitNot: 0,

	BinaryOpType.Mul: 1,
	BinaryOpType.Div: 1,
	BinaryOpType.Mod: 1,

	BinaryOpType.Add: 2,
	BinaryOpType.Sub: 2,

	BinaryOpType.Shl: 3,
	BinaryOpType.Shr: 3,

	BinaryOpType.Lt: 4,
	BinaryOpType.Lte: 4,
	BinaryOpType.Gt: 4,
	BinaryOpType.Gte: 4,

	BinaryOpType.Eq: 5,
	BinaryOpType.Neq: 5,

	BinaryOpType.BitAnd: 6,

	BinaryOpType.BitXor: 7,

	BinaryOpType.BitOr: 8,

	BinaryOpType.And: 9,

	BinaryOpType.Or: 10,

	# lowest precedence
}