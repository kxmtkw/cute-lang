from Compiler.lexer.tokens import Token, TokenType

from Compiler.parser.nodes import Node


class Parser:


	def __init__(self, tokens: list[Token]) -> None:
		self.tokens = tokens
		self.pos = 0
		self.length = len(tokens)


	def peek(self, offset: int = 0) -> Token:
		idx = self.pos + offset
		if idx >= self.length:
			return Token(TokenType.EOF)
		return self.tokens[idx]


	def advance(self, steps: int = 1) -> Token:
		tok = self.peek()
		self.pos += steps
		return tok

	
	def parse(self):
		while self.peek().type != TokenType.EOF:
			self.parse_expression()

	def parse_function(self):
		pass 

	def parse_expression(self) -> Node.Expression:
		pass 