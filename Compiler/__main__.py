import sys
from Compiler.lexer.lexer import Lexer


def main():
	filepath = sys.argv[1] 

	with open(filepath) as file:
		content = file.read()

	lexer = Lexer(content)
	tokens = lexer.tokenize()

	print("\n" + "-"*10 + "\n")

	for token in tokens:
		print(token)

	print("\n" + "-"*10 + "\n")


if __name__ == "__main__":
	main()