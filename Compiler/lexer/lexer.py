from typing import List, Optional

from Compiler.lexer.tokens import Token, TokenType, SymbolType, KeywordType, KEYWORD_MAP, SYMBOL_MAP


class Lexer:


	def __init__(self, source: str):
		self.source = source
		self.pos = 0
		self.length = len(source)


	def _peek(self, offset: int = 0) -> str:
		idx = self.pos + offset
		if idx >= self.length:
			return ""
		return self.source[idx]


	def _advance(self, steps: int = 1) -> str:
		ch = self._peek()
		self.pos += steps
		return ch


	def tokenize(self) -> List[Token]:
		tokens = []
		while self.pos < self.length:
			ch = self._peek()

			if ch in " \t\r":
				self._advance()
				continue

			if ch == "\n":
				self._advance()
				tokens.append(Token(TokenType.EOL, "\n"))
				continue

			if ch == "/" and self._peek(1) == "/":
				self._skip_comments()
				continue

			if ch == '"':
				tokens.append(self._lex_string())
				continue

			if ch == "'":
				tokens.append(self._lex_char())
				continue

			if ch.isdigit():
				tokens.append(self._lex_number())
				continue

			if ch.isalpha() or ch == "_":
				tokens.append(self._lex_word_or_keyword_or_bool())
				continue

			symbol_token = self._lex_symbol()
			if symbol_token:
				tokens.append(symbol_token)
				continue

			raise ValueError(f"Unexpected character '{ch}' at index {self.pos}")

		tokens.append(Token(TokenType.EOF, None))
		return tokens


	def _skip_comments(self):
		if self._peek(0) == "/" and self._peek(1) == "/" and self._peek(2) == "/":
			self._advance(3)
			while self.pos < self.length:
				if self._peek(0) == "/" and self._peek(1) == "/" and self._peek(2) == "/":
					self._advance(3)
					break
				self._advance()
		else:
			self._advance(2)
			while self.pos < self.length and self._peek() != "\n":
				self._advance()


	def _lex_number(self) -> Token:
		start = self.pos
		if self._peek() == "0":
			next_ch = self._peek(1).lower()
			if next_ch == "x":
				self._advance(2)
				while self.pos < self.length and (self._peek().isdigit() or self._peek().lower() in "abcdef"):
					self._advance()
				val = int(self.source[start:self.pos], 16)
				return Token(TokenType.HEX, val)
			elif next_ch == "b":
				self._advance(2)
				while self.pos < self.length and self._peek() in "01":
					self._advance()
				val = int(self.source[start:self.pos], 2)
				return Token(TokenType.BIN, val)

		is_float = False
		while self.pos < self.length:
			if self._peek().isdigit():
				self._advance()
			elif self._peek() == "." and not is_float and self._peek(1).isdigit():
				is_float = True
				self._advance()
			else:
				break

		num_str = self.source[start:self.pos]
		if is_float:
			return Token(TokenType.FLOAT, float(num_str))
		return Token(TokenType.INT, int(num_str))


	def _lex_string(self) -> Token:
		self._advance()
		start = self.pos
		while self.pos < self.length and self._peek() != '"':
			self._advance()
		if self.pos >= self.length:
			raise ValueError("Unterminated string literal")
		val = self.source[start:self.pos]
		self._advance()
		return Token(TokenType.STRING, val)


	def _lex_char(self) -> Token:
		self._advance()
		val = self._advance()
		if self._peek() != "'":
			raise ValueError("Unterminated or multi-character char literal")
		self._advance()
		return Token(TokenType.CHAR, val)


	def _lex_word_or_keyword_or_bool(self) -> Token:
		start = self.pos
		while self.pos < self.length and (self._peek().isalnum() or self._peek() == "_"):
			self._advance()
		text = self.source[start:self.pos]

		if text == "true":
			return Token(TokenType.BOOL, True)
		if text == "false":
			return Token(TokenType.BOOL, False)
		if text in KEYWORD_MAP:
			return Token(TokenType.KEYWORD, KEYWORD_MAP[text])
		return Token(TokenType.WORD, text)


	def _lex_symbol(self) -> Optional[Token]:
		two_char = self.source[self.pos:self.pos+2]
		if two_char in SYMBOL_MAP:
			self._advance(2)
			return Token(TokenType.SYMBOL, SYMBOL_MAP[two_char])

		one_char = self._peek()
		if one_char in SYMBOL_MAP:
			self._advance(1)
			return Token(TokenType.SYMBOL, SYMBOL_MAP[one_char])

		return None