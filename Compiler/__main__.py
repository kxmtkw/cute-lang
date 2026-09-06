import sys
from Compiler.lexer.lexer import Lexer
from Compiler.parser.parser import Parser
from Compiler.resolver.resolver import Resolver
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

	resolver = Resolver()
	resolver.visit(program)

	print("\n" + "-"*10 + "\n")

	outpath = filepath.removesuffix(".ct") + ".cute"
	gen = CodeGenerator(outpath)
	gen.visit(program)

	print(f"--- Program Image written to {outpath}")


if __name__ == "__main__":
	main()