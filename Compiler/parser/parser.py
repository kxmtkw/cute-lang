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


	def expect_token_type(self, type: TokenType, panic: bool = False) -> Token | None:
		if self.peek().type == type:
			return self.advance()

		if panic:
			print(f"Expected {type.name}, got {self.peek().type}")
			exit(1)


	def expect_keyword(self, kw: KeywordType, panic: bool = False) -> Token | None:
		if self.peek().type == TokenType.Keyword and self.peek().value == kw:
			return self.advance()

		if panic:
			print(f"Expected {kw.value}, got {self.peek().value}")
			exit(1)


	def expect_symbol(self, sym: SymbolType, panic: bool = False) -> Token | None:
		if self.peek().type == TokenType.Symbol and self.peek().value == sym:
			return self.advance()

		if panic:
			print(f"Expected {sym.value}, got {self.peek().value}")
			exit(1)

	
	def parse(self):
		nodes = []

		while self.peek().type != TokenType.EOF:
			stmt = self.parse_statement()
			if stmt: nodes.append(stmt)

		main = Node.Function(
			"main",
			[],
			nodes
		)

		program = Node.Program(
			[main]
		)

		return program


	def parse_statement(self) -> Node.Expression:

		while self.expect_token_type(TokenType.EOL) or self.expect_symbol(SymbolType.Semicolon):
			continue
		
		if self.expect_keyword(KeywordType.Let):
			self.backtrack()
			node = self.parse_decl()
		else:
			node = self.parse_expression()

		while self.expect_token_type(TokenType.EOL) or self.expect_symbol(SymbolType.Semicolon):
			continue

		return node
		

	def parse_expression(self, prev_bp: float = -2) -> Node.Expression:

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

			symbol = self.expect_token_type(TokenType.Symbol, True)

			if symbol is None:
				raise ValueError("Expected symbol.")
			
			if symbol.value in r.STATEMENT_ENDERS:
				self.backtrack()
				return lhs

			if symbol.value == SymbolType.LParen:
				self.backtrack()
				if prev_bp >= r.PARENTHESIS_INFIX_BP:
					return lhs
				lhs = self.parse_call(lhs)
				continue

			# symbol token will always be a token, do not need to check it here
			operation = r.BINARY_OPERATOR_MAPPING.get(symbol.value, r.UNARY_OP_MAPPING.get(symbol)) # type: ignore

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
			return Node.Literal(token.value) # type: ignore

		if token.type == TokenType.Word:

			self.advance()

			return Node.Identifier(token.value) # type: ignore

		raise ValueError(f"Expected atomic expression! Got {self.peek().type}")


	def parse_call(self, callee: Node.Expression) -> Node.Call:

		self.expect_symbol(SymbolType.LParen, True)

		args = []

		while self.expect_symbol(SymbolType.RParen) is None:
			args.append(self.parse_expression())
			self.expect_symbol(SymbolType.Comma, True)

		return Node.Call(
			callee,
			args
		)


	def parse_decl(self) -> Node.Declaration:

		self.expect_keyword(KeywordType.Let, True)

		name = self.expect_token_type(TokenType.Word, True)

		if self.expect_symbol(SymbolType.Colon):
			decl_type = self.expect_token_type(TokenType.Word, True).value # type: ignore
		else:
			decl_type = None

		if self.expect_symbol(SymbolType.Assign):
			value = self.parse_expression()
		else:
			value = None

		return Node.Declaration(name.value, decl_type, value)  # type: ignore
