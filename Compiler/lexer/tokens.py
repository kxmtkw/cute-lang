from enum import Enum, auto
from typing import Union, List, Optional


class TokenType(Enum):
	INT = auto()
	HEX = auto()
	BIN = auto()
	FLOAT = auto()
	BOOL = auto()
	WORD = auto()
	STRING = auto()
	CHAR = auto()
	SYMBOL = auto()
	KEYWORD = auto()
	EOL = auto()
	EOF = auto()


class KeywordType(Enum):
	FUNC = "func"
	LET = "let"
	CONTAINER = "container"
	RAW = "raw"
	ATOM = "atom"


class SymbolType(Enum):
	PLUS = "+"
	MINUS = "-"
	STAR = "*"
	DSTAR = "**"
	SLASH = "/"
	LPAREN = "("
	RPAREN = ")"
	LBRACKET = "["
	RBRACKET = "]"
	LBRACE = "{"
	RBRACE = "}"
	BANG = "!"
	ASSIGN = "="
	EQ = "=="
	NEQ = "!="
	GTE = ">="
	LTE = "<="
	LT = "<"
	GT = ">"
	DOUBLELT = "<<"
	DOUBLEGT = ">>"
	PERCENT = "%"
	CARET = "^"
	AMP = "&"
	PIPE = "|"
	AND = "&&"
	OR = "||"
	COLON = ":"
	SEMICOLON = ";"
	COMMA = ","
	DOT = "."
	HASHTAG = "#"


KEYWORD_MAP = {k.value: k for k in KeywordType}
SYMBOL_MAP = {s.value: s for s in SymbolType}


TokenValue = Union[int, float, bool, str, SymbolType, KeywordType, None]


class Token:
	
	def __init__(self, token_type: TokenType, value: TokenValue = None):
		self.type = token_type
		self.value = value

	def __repr__(self):
		return f"Token({self.type.name}, {self.value!r})"
