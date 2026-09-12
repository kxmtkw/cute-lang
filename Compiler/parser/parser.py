from Compiler.defs.expr import ExprLiteralType
from Compiler.lexer.defs import KeywordType, SymbolType, Token, TokenType

from Compiler.defs.nodes import Node
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

			if self.expect_keyword(KeywordType.Container):
				self.backtrack()
				func = self.parse_container()
				nodes.append(func)
				continue

			raise ValueError(f"Unexpected token: {self.peek()}")
		
		program = Node.Program(nodes)

		return program


	def parse_statement(self) -> Node.Expression:

		self.eat_stmt_enders()

		handlers: dict = {
			KeywordType.Let:     self.parse_decl,
			KeywordType.If:      self.parse_if,
			KeywordType.While:   self.parse_while,
			KeywordType.For:     self.parse_for,
			KeywordType.Return:  self.parse_return,
			KeywordType.Builtin: self.parse_builtin,
			SymbolType.LBrace:   self.parse_block,
		}

		current_token = self.peek()

		if current_token.value in handlers:
			node = handlers[current_token.value]()
		else:
			node = self.parse_expression()

		return node
		

	def parse_expression(self, prev_bp: float = 0) -> Node.Expression:

		symbol_token = self.expect_token_type(TokenType.Symbol)

		if symbol_token is None:
			lhs = self.parse_atom()

		elif symbol_token.value == SymbolType.LParen:
			lhs = self.parse_expression()
			if self.expect_symbol(SymbolType.RParen) is None:
				raise ValueError("Unterminated paran.")

		elif symbol_token.value in r.UNARY_OP_MAPPING:
			unary = r.UNARY_OP_MAPPING[symbol_token.value]
			l_bp, r_bp = r.OPERATOR_BINDING_POWER[unary]
			lhs = self.parse_expression(r_bp)
			lhs = Node.UnaryOp(
				unary,
				lhs
			)

		else:
			raise ValueError(f"Unexpected token {self.peek()}")
	

		while True:

			if self.expect_token_type(TokenType.EOL) or self.expect_token_type(TokenType.EOF) or self.peek().value in r.STATEMENT_ENDERS:
				return lhs

			symbol_token = self.expect_token_type(TokenType.Symbol, True)

			if symbol_token is None:
				raise ValueError("Expected symbol.")

			if symbol_token.value == SymbolType.LParen:
				self.backtrack()
				if prev_bp >= r.PARENTHESIS_INFIX_BP:
					return lhs
				lhs = self.parse_call(lhs)
				continue

			operation = r.BINARY_OPERATOR_MAPPING.get(symbol_token.extract(SymbolType))

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
		token = self.advance()

		if token.type in (TokenType.Int, TokenType.Hex, TokenType.Bin):
			return Node.Literal(token.extract(int), ExprLiteralType.Int)

		elif token.type == TokenType.Float:
			return Node.Literal(token.extract(float), ExprLiteralType.Float)

		elif token.type == TokenType.Bool:
			return Node.Literal(token.extract(int), ExprLiteralType.Bool)

		elif token.type == TokenType.Char:
			return Node.Literal(token.extract(str), ExprLiteralType.Char)

		elif token.type == TokenType.String:
			return Node.Literal(token.extract(str), ExprLiteralType.String)

		elif token.type == TokenType.Word:
			return Node.Identifier(token.extract(str))

		else:
			raise ValueError(f"Expected atomic expression! Got {token}")


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
	

	def parse_decl(self, *, type_must_be_specified: bool = False, let_required: bool = True, no_value: bool = False) -> Node.Declaration:

		self.expect_keyword(KeywordType.Let, let_required)

		name_token = self.expect_token_type(TokenType.Word, True)
		assert name_token is not None
		name = name_token.extract(str)

		if self.expect_symbol(SymbolType.Colon):
			decl_type_token = self.expect_token_type(TokenType.Word, True)
			assert decl_type_token is not None
			decl_type = decl_type_token.extract(str)
		else:
			if type_must_be_specified:
				raise ValueError("Type must be specified for this declaration.")
			decl_type = None


		if self.expect_symbol(SymbolType.Equal) and not no_value:
			value = self.parse_expression()
		else:
			value = None

		return Node.Declaration(name, decl_type, value)


	def parse_if(self) -> Node.If:

		self.expect_keyword(KeywordType.If, True)

		condition = self.parse_expression()
		
		then_block = self.parse_block()

		if self.expect_keyword(KeywordType.Else) is not None:
			else_stmt = self.parse_statement()	
		else:
			else_stmt = None

		return Node.If(condition, then_block, else_stmt)


	def parse_while(self) -> Node.While:

		self.expect_keyword(KeywordType.While, True)

		condition = self.parse_expression()
		
		block = self.parse_block()

		return Node.While(condition, block)


	def parse_for(self) -> Node.For:
	
		self.expect_keyword(KeywordType.For, True)

		init = self.parse_statement()
		self.expect_symbol(SymbolType.Comma, True)
		condition = self.parse_expression()
		self.expect_symbol(SymbolType.Comma, True)
		step = self.parse_expression()
		
		block = self.parse_block()

		return Node.For(init, condition, step, block)


	def parse_return(self) -> Node.Return:

		self.expect_keyword(KeywordType.Return, True)

		if self.expect_symbol(SymbolType.Semicolon) or self.peek().type == TokenType.EOL:
			return Node.Return()

		value = self.parse_expression()

		return Node.Return(value)

	
	def parse_func(self) -> Node.Function:

		self.expect_keyword(KeywordType.Func, True)
		name_token = self.expect_token_type(TokenType.Word, True)
		assert name_token is not None
		name = name_token.extract(str)

		self.expect_symbol(SymbolType.LParen, True)

		params = []

		while True:
			if self.expect_symbol(SymbolType.RParen):
				break
			params.append(self.parse_decl(type_must_be_specified=True, let_required=False))
			self.expect_symbol(SymbolType.Comma, False)


		if self.expect_symbol(SymbolType.Arrow):
			return_type = self.expect_token_type(TokenType.Word, True)
			return_type = return_type.extract(str) if return_type is not None else None
		else:
			return_type = None

		self.eat_stmt_enders()

		body = self.parse_block()

		return Node.Function(name, params, body, return_type)


	def parse_builtin(self) -> Node.BuiltinCommand:

		self.expect_keyword(KeywordType.Builtin)

		args: list[Node.Identifier] = []

		while not (self.expect_symbol(SymbolType.Semicolon) or self.expect_token_type(TokenType.EOL)):
			token = self.expect_token_type(TokenType.Word, True)
			assert token is not None
			args.append(Node.Identifier(token.extract(str)))

		return Node.BuiltinCommand(args)


	def parse_container(self) -> Node.Container:

		self.expect_keyword(KeywordType.Container)

		name_token = self.expect_token_type(TokenType.Word, True)
		assert name_token is not None
		name = name_token.extract(str)

		if self.expect_symbol(SymbolType.Star):
			return Node.Container(
				name,
				True,
				[]
			)

		self.expect_symbol(SymbolType.LBrace)
		fields = []

		while not self.expect_symbol(SymbolType.RBrace):
			self.eat_stmt_enders()
			fields.append(self.parse_decl(type_must_be_specified=True, let_required=False, no_value=True))

			if self.expect_symbol(SymbolType.Comma):
				continue
			
			self.eat_stmt_enders()
			if self.expect_symbol(SymbolType.RBrace):
				break
			

		return Node.Container(
			name,
			False,
			fields
		)
			


