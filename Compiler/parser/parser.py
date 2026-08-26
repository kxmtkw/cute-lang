from Compiler.lexer.tokens import KeywordType, SymbolType, Token, TokenType

from Compiler.parser.nodes import Node
import Compiler.parser.rules as r

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


	def backtrack(self, steps: int = 1):
		self.pos -= steps


	def expect_token_type(self, type: TokenType) -> Token | None:
		if self.peek().type == type:
			return self.advance()


	def expect_keyword(self, kw: KeywordType) -> Token | None:
		if self.peek().type == TokenType.Keyword and self.peek().value == kw:
			return self.advance()


	def expect_symbol(self, sym: SymbolType) -> Token | None:
		if self.peek().type == TokenType.Symbol and self.peek().value == sym:
			return self.advance()

	
	def parse(self):
		nodes = []
		while self.peek().type != TokenType.EOF:
			if self.expect_token_type(TokenType.EOL):
				continue
			nodes.append(self.parse_expression())

		return nodes

	
	def parse_expression(self, prev_bp: int = -2) -> Node.Expression | None:

		sym = self.expect_token_type(TokenType.Symbol)

		if sym is None:
			lhs = self.parse_atom()

		elif sym.value == SymbolType.LParen:
			lhs = self.parse_expression(0)
			if self.expect_symbol(SymbolType.RParen) is None:
				raise ValueError("Unterminated paran.")

		elif sym.value in r.UNARY_OP_MAPPING:
			unary = r.UNARY_OP_MAPPING[sym.value]
			l_bp, r_bp = r.OPERATOR_BINDING_POWER[unary]
			lhs = self.parse_expression(r_bp)
			lhs = Node.UnaryOp(
				unary,
				lhs
			)

		else:
			raise ValueError(f"Unexpected token {self.peek()}")

		while True:

			if self.peek().type in [
				TokenType.EOF,
				TokenType.EOL
			]:
				return lhs

			symbol = self.expect_token_type(TokenType.Symbol)

			if symbol.value in [
				SymbolType.RParen,
				SymbolType.Semicolon,
				SymbolType.Comma
			]:
				self.backtrack()
				return lhs

			if symbol.value == SymbolType.LParen:
				self.backtrack()
				if prev_bp >= r.PARENTHESIS_INFIX_BP:
					return lhs
				lhs = self.parse_call(lhs)
				continue
			
			operation = r.BINARY_OPERATOR_MAPPING.get(
				symbol.value,
				r.UNARY_OP_MAPPING.get(symbol)
			)

			if operation is None:
				raise ValueError(f"Unknown token: {self.peek()}")

			l_bp, r_bp = r.OPERATOR_BINDING_POWER[operation]

			if prev_bp > l_bp:
				self.backtrack()
				return lhs

			lhs = Node.BinaryOp(
				operation,
				lhs,
				self.parse_expression(r_bp)
			)


	def parse_atom(self) -> Node.Expression:

		token = self.peek()

		if token.type in [
			TokenType.Int,
			TokenType.Hex,
			TokenType.Bin,
			TokenType.Float,
			TokenType.Bool,
			TokenType.Char,
			TokenType.String
		]:
			self.advance()
			return Node.Literal(
				token.value
			)

		if token.type == TokenType.Word:

			self.advance()

			return Node.Identifier(
				token.value
			)


	def parse_call(self, callee: Node.Expression) -> Node.Call:

		self.expect_symbol(SymbolType.LParen)

		args = []

		while self.expect_symbol(SymbolType.RParen) is None:
			args.append(self.parse_expression())
			self.expect_symbol(SymbolType.Comma)

		return Node.Call(
			callee,
			args
		)

		

