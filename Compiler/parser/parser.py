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
		print(tok)
		self.pos += steps
		return tok


	def backtrack(self, steps: int = 1):
		self.pos -= steps


	def expect_token_type(self, type: TokenType, panic: bool = False) -> Token | None:
		if self.peek().type == type:
			return self.advance()

		if panic:
			print(f"Expected {type.name}, got {self.peek()}")
			exit(1)


	def expect_keyword(self, kw: KeywordType, panic: bool = False) -> Token | None:
		if self.peek().type == TokenType.Keyword and self.peek().value == kw:
			return self.advance()

		if panic:
			print(f"Expected {kw.value}, got {self.peek()}")
			exit(1)


	def expect_symbol(self, sym: SymbolType, panic: bool = False) -> Token | None:
		if self.peek().type == TokenType.Symbol and self.peek().value == sym:
			return self.advance()

		if panic:
			print(f"Expected {sym.value}, got {self.peek().value}")
			exit(1)


	def eat_stmt_enders(self):
		while self.peek().type == TokenType.EOL or self.expect_symbol(SymbolType.Semicolon):
			self.advance()


	def parse(self):

		nodes = []

		while self.peek().type != TokenType.EOF:
			self.eat_stmt_enders()

			if self.expect_keyword(KeywordType.Func):
				self.backtrack()
				func = self.parse_func()
				nodes.append(func)
				continue

		program = Node.Program(nodes)

		return program


	def parse_statement(self) -> Node.Expression:

		self.eat_stmt_enders()

		if self.expect_keyword(KeywordType.Let):
			self.backtrack()
			node = self.parse_decl()
		elif self.expect_keyword(KeywordType.If):
			self.backtrack()
			node = self.parse_if()
		elif self.expect_keyword(KeywordType.While):
			self.backtrack()
			node = self.parse_while()
		elif self.expect_keyword(KeywordType.Return):
			self.backtrack()
			node = self.parse_return()
		elif self.expect_symbol(SymbolType.LBrace):
			self.backtrack()
			node = self.parse_block()
		else:
			node = self.parse_expression()

		self.eat_stmt_enders()

		return node
		

	def parse_expression(self, prev_bp: float = 0) -> Node.Expression:

		sym = self.expect_token_type(TokenType.Symbol)

		if sym is None:
			lhs = self.parse_atom()

		elif sym.value == SymbolType.LParen:
			lhs = self.parse_expression()
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

		raise ValueError(f"Expected atomic expression! Got {self.peek()}")


	def parse_call(self, callee: Node.Expression) -> Node.Call:

		self.expect_symbol(SymbolType.LParen, True)

		args = []

		while self.expect_symbol(SymbolType.RParen) is None:
			args.append(self.parse_expression())
			if not self.expect_symbol(SymbolType.Comma):
				self.expect_symbol(SymbolType.RParen, True)
				break

		return Node.Call(
			callee,
			args
		)


	def parse_block(self) -> Node.Block:

		self.expect_symbol(SymbolType.LBrace)

		stmts = []
		while self.expect_symbol(SymbolType.RBrace) is None:
			stmts.append(self.parse_statement())

		return Node.Block(stmts)
	

	def parse_decl(self, *, type_must_be_specified: bool = False) -> Node.Declaration:

		self.expect_keyword(KeywordType.Let, False)

		name = self.expect_token_type(TokenType.Word, True)

		if self.expect_symbol(SymbolType.Colon):
			decl_type = self.expect_token_type(TokenType.Word, True).value # type: ignore
		else:
			if type_must_be_specified:
				raise ValueError("Type must be specified for this declaration.")
			decl_type = None

		if self.expect_symbol(SymbolType.Assign):
			value = self.parse_expression()
		else:
			value = None

		return Node.Declaration(name.value, decl_type, value)  # type: ignore


	def parse_if(self) -> Node.Declaration:

		self.expect_keyword(KeywordType.If, True)

		condition = self.parse_expression()
		
		then_block = self.parse_statement()

		if self.expect_keyword(KeywordType.Else) is not None:
			else_stmt = self.parse_statement()	
		else:
			else_stmt = False

		return Node.If(condition, then_block, else_stmt)  # type: ignore


	def parse_while(self) -> Node.While:

		self.expect_keyword(KeywordType.While, True)

		condition = self.parse_expression()
		
		block = self.parse_block()

		return Node.While(condition, block)



	def parse_return(self) -> Node.Return:

		self.expect_keyword(KeywordType.Return, True)

		if self.expect_symbol(SymbolType.Semicolon) or self.peek().type == TokenType.EOL:
			return Node.Return()

		value = self.parse_expression()

		return Node.Return(value)

	
	def parse_func(self) -> Node.Function:

		self.expect_keyword(KeywordType.Func, True)
		name = self.expect_token_type(TokenType.Word, True)

		self.expect_symbol(SymbolType.LParen, True)

		params = []

		while True:
			if self.expect_symbol(SymbolType.RParen):
				break
			params.append(self.parse_decl(type_must_be_specified=True))
			self.expect_symbol(SymbolType.Comma, False)


		if self.expect_symbol(SymbolType.Arrow):
			return_type = self.expect_token_type(TokenType.Word, True)
			return_type = return_type.value if return_type is not None else None
		else:
			return_type = None

		self.eat_stmt_enders()

		body = self.parse_block()

		return Node.Function(name.value, params, body, return_type)

