from enum import Enum, auto
from typing import Union, List, Optional

class KeywordType(Enum):
	Func = "func"
	Return = "return"
	Let = "let"
	Container = "container"
	BoolTrue = "true"
	BoolFalse = "false"
	While = "while"
	For = "for"
	If = "if"
	Else = "else"
	Builtin = "__builtin__"


class SymbolType(Enum):
	Plus = "+"
	Minus = "-"
	Star = "*"
	DStar = "**"
	Slash = "/"
	LParen = "("
	RParen = ")"
	LBracket = "["
	RBracket = "]"
	LBrace = "{"
	RBrace = "}"
	Bang = "!"
	Assign = "="
	Eq = "=="
	Neq = "!="
	Gte = ">="
	Lte = "<="
	Lt = "<"
	Gt = ">"
	DoubleLt = "<<"
	DoubleGt = ">>"
	Percent = "%"
	Caret = "^"
	Amp = "&"
	Pipe = "|"
	And = "&&"
	Or = "||"
	Colon = ":"
	Semicolon = ";"
	Comma = ","
	Dot = "."
	Hashtag = "#"
	Arrow = "->"


KEYWORD_MAP = {k.value: k for k in KeywordType}
SYMBOL_MAP = {s.value: s for s in SymbolType}


class TokenType(Enum):
	Int = auto()
	Hex = auto()
	Bin = auto()
	Float = auto()
	Bool = auto()
	Word = auto()
	String = auto()
	Char = auto()
	Symbol = auto()
	Keyword = auto()
	EOL = auto()
	EOF = auto()


TokenValue = Union[int, float, bool, str, SymbolType, KeywordType, None]

class Token:
	
	def __init__(self, token_type: TokenType, value: TokenValue = None):
		self.type = token_type
		self.value = value

	def __repr__(self):
		return f"Token({self.type.name}, {self.value!r})"