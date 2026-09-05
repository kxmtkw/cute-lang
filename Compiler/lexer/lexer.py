from typing import List, Optional

from Compiler.lexer.defs import Token, TokenType, SymbolType, KeywordType, KEYWORD_MAP, SYMBOL_MAP



class Lexer:


	def __init__(self, source: str):
		self.source = source
		self.pos = 0
		self.length = len(source)


	def peek(self, offset: int = 0) -> str:
		idx = self.pos + offset
		if idx >= self.length:
			return ""
		return self.source[idx]


	def advance(self, steps: int = 1) -> str:
		ch = self.peek()
		self.pos += steps
		return ch


	def tokenize(self) -> List[Token]:
		
		tokens = []
		while self.pos < self.length:
			ch = self.peek()

			if ch in " \t\r":
				self.advance()
				continue

			if ch == "\n":
				self.advance()
				tokens.append(Token(TokenType.EOL, "\n"))
				continue

			if ch == "/" and self.peek(1) == "/":
				self.skip_comments()
				continue

			if ch == '"':
				tokens.append(self.lex_string())
				continue

			if ch == "'":
				tokens.append(self.lex_char())
				continue

			if ch.isdigit():
				tokens.append(self.lex_number())
				continue

			if ch.isalpha() or ch == "_":
				tokens.append(self.lex_word_or_keyword_or_bool())
				continue

			symbol_token = self.lex_symbol()
			if symbol_token:
				tokens.append(symbol_token)
				continue

			raise ValueError(f"Unexpected character '{ch}' at index {self.pos}")

		tokens.append(Token(TokenType.EOF, None))
		return tokens


	def skip_comments(self):
		
		if self.peek(0) == "/" and self.peek(1) == "/" and self.peek(2) == "/":
			self.advance(3)
			while self.pos < self.length:
				if self.peek(0) == "/" and self.peek(1) == "/" and self.peek(2) == "/":
					self.advance(3)
					break
				self.advance()
		else:
			self.advance(2)
			while self.pos < self.length and self.peek() != "\n":
				self.advance()


	def lex_number(self) -> Token:
		
		start = self.pos

		if self.peek() == "0":
			next_ch = self.peek(1).lower()

			if next_ch == "x":
				self.advance(2)
				while self.pos < self.length and (self.peek().isdigit() or self.peek().lower() in "abcdef"):
					self.advance()
				val = int(self.source[start:self.pos], 16)
				return Token(TokenType.Hex, val)

			elif next_ch == "b":
				self.advance(2)
				while self.pos < self.length and self.peek() in "01":
					self.advance()
				val = int(self.source[start:self.pos], 2)
				return Token(TokenType.Bin, val)

		is_float = False

		while self.pos < self.length:
			if self.peek().isdigit():
				self.advance()
			elif self.peek() == "." and not is_float and self.peek(1).isdigit():
				is_float = True
				self.advance()
			else:
				break

		num_str = self.source[start:self.pos]

		if is_float:
			return Token(TokenType.Float, float(num_str))

		return Token(TokenType.Int, int(num_str))


	def lex_string(self) -> Token:
		
		self.advance()
		start = self.pos

		while self.pos < self.length and self.peek() != '"':
			self.advance()

		if self.pos >= self.length:
			raise ValueError("Unterminated string literal")

		val = self.source[start:self.pos]
		self.advance()
		return Token(TokenType.String, val)


	def lex_char(self) -> Token:
		
		self.advance()
		val = self.advance()
		if self.peek() != "'":
			raise ValueError("Unterminated or multi-character char literal")
		self.advance()
		return Token(TokenType.Char, val)


	def lex_word_or_keyword_or_bool(self) -> Token:
		
		start = self.pos
		while self.pos < self.length and (self.peek().isalnum() or self.peek() == "_"):
			self.advance()
		text = self.source[start:self.pos]

		if text == KeywordType.BoolTrue.value:
			return Token(TokenType.Bool, True)
		if text == KeywordType.BoolFalse.value:
			return Token(TokenType.Bool, False)
		if text in KEYWORD_MAP:
			return Token(TokenType.Keyword, KEYWORD_MAP[text])
		return Token(TokenType.Word, text)


	def lex_symbol(self) -> Optional[Token]:
		
		if self.pos + 1 < self.length:
			two_char = self.source[self.pos:self.pos + 2]
			if two_char in SYMBOL_MAP:
				self.advance(2)
				return Token(TokenType.Symbol, SYMBOL_MAP[two_char])

		one_char = self.peek()
		if one_char in SYMBOL_MAP:
			self.advance(1)
			return Token(TokenType.Symbol, SYMBOL_MAP[one_char])

		return None