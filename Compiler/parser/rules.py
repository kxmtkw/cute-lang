from typing import Union

from Compiler.lexer.defs import SymbolType, TokenType
from Compiler.defs.op import BinaryOpType, UnaryOpType


BINARY_OPERATOR_MAPPING: dict[SymbolType, BinaryOpType] = {
	SymbolType.Equal: BinaryOpType.Assign,
	SymbolType.Dot: BinaryOpType.Access,
	SymbolType.Plus: BinaryOpType.Add,
	SymbolType.Minus: BinaryOpType.Sub,
	SymbolType.Star: BinaryOpType.Mul,
	SymbolType.Slash: BinaryOpType.Div,
	SymbolType.Percent: BinaryOpType.Mod,
	SymbolType.DEqual: BinaryOpType.Eq,
	SymbolType.NEqual: BinaryOpType.Neq,
	SymbolType.Lt: BinaryOpType.Lt,
	SymbolType.Gt: BinaryOpType.Gt,
	SymbolType.Lte: BinaryOpType.Lte,
	SymbolType.Gte: BinaryOpType.Gte,
	SymbolType.DAmp: BinaryOpType.And,
	SymbolType.DPipe: BinaryOpType.Or,
	SymbolType.Amp: BinaryOpType.BitAnd,
	SymbolType.Pipe: BinaryOpType.BitOr,
	SymbolType.Caret: BinaryOpType.BitXor,
	SymbolType.DoubleLt: BinaryOpType.Shl,
	SymbolType.DoubleGt: BinaryOpType.Shr,
}


UNARY_OP_MAPPING: dict[SymbolType, UnaryOpType] = {
	SymbolType.Minus: UnaryOpType.Negate,
	SymbolType.Bang: UnaryOpType.Not,
	SymbolType.Caret: UnaryOpType.BitNot,
}


OPERATOR_BINDING_POWER: dict[Union[BinaryOpType, UnaryOpType], tuple[float, float]] = {
	BinaryOpType.Assign: (0.2, 0.1),
	BinaryOpType.Or: (0.8, 0.9),
	BinaryOpType.And: (1, 1.1),
	BinaryOpType.BitOr: (2, 2.1),
	BinaryOpType.BitXor: (3, 3.1),
	BinaryOpType.BitAnd: (4, 4.1),
	BinaryOpType.Eq: (5, 5.1),
	BinaryOpType.Neq: (5, 5.1),
	BinaryOpType.Lt: (6, 6.1),
	BinaryOpType.Lte: (6, 6.1),
	BinaryOpType.Gt: (6, 6.1),
	BinaryOpType.Gte: (6, 6.1),
	BinaryOpType.Shl: (7, 7.1),
	BinaryOpType.Shr: (7, 7.1),
	BinaryOpType.Add: (8, 8.1),
	BinaryOpType.Sub: (8, 8.1),
	BinaryOpType.Mul: (9, 9.1),
	BinaryOpType.Div: (9, 9.1),
	BinaryOpType.Mod: (9, 9.1),
	UnaryOpType.Negate: (11.1, 11),
	UnaryOpType.Not: (11.1, 11),
	UnaryOpType.BitNot: (11.1, 11),
	BinaryOpType.Access: (12, 12.1)
}

PARENTHESIS_INFIX_BP = 11.9

STATEMENT_ENDERS = [
	SymbolType.RParen,
	SymbolType.LBrace,
	SymbolType.RBrace,
	SymbolType.RBracket,
	SymbolType.Semicolon,
	SymbolType.Comma
]