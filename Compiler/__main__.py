import sys
from Compiler.lexer.lexer import Lexer
from Compiler.parser.parser import Parser
from Compiler.codegen.generator import CodeGenerator


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
	program = parser.parse()
	print(program.dump())

	print("\n" + "-"*10 + "\n")

	gen = CodeGenerator()
	gen.visit(program)


if __name__ == "__main__":
	main()