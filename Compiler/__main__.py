import sys
from Compiler.lexer.lexer import Lexer
from Compiler.parser.parser import Parser

def main():
	filepath = sys.argv[1] 

	with open(filepath) as file:
		content = file.read()


	print("\n" + "-"*10 + "\n")

	lexer = Lexer(content)
	tokens = lexer.tokenize()
	
	for token in tokens:
		print(token)

	print("\n" + "-"*10 + "\n")

	parser = Parser(tokens)

	for d in parser.parse():
		print(d.dump())

	print("\n" + "-"*10 + "\n")


if __name__ == "__main__":
	main()