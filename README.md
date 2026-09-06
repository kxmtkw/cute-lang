
<h1 align="center">Cute (,,>﹏<,,)</h1>

`Cute` is a cute little language that I am working on. It comes with its own instruction set, compiler and the core runtime.

### Features
Some planned/present features:

- `Multi-Paradigm language` with support for both objects and functional styles.
- `Automatic Memory Management` with a garbage collector.
- `Easy Syntax` inspired from C and Python.


### Example

Make a `demo.ct` file in your project. Write the following code in it.

```c

func exit(code: int) {
	__builtin__ instr halt code
}

func print(x: int) {
	__builtin__ out int x
	return
}

func factorial(x: int) -> int {
	if x - 1 {
		return x * factorial(x - 1)
	}
	return 1
}

func main() { 
	let z: int = 5
	let f: int = factorial(z)
	print(f)
	exit(0)
}
```

Then compile the file using:
```bash
python3 -m Compiler demo.ct
```

This will output a `demo.cute` file. Simply run that file using the runtime.
```bash
cute demo.cute
# output: [ int 120 ]
```

### Installing

No official installation exists since the project is still in its infant stage.

1. Clone the repository.
2. Build the project. See [Building Cute](docs/04-building.md).


### Docs
Here is a list of documentation to get you started:

1. [Project Architecture](docs/01-arch.md)
2. [Instruction Set](docs/02-instructions.md)
3. [Image Format](docs/03-image.md)
4. [Building Cute](docs/04-building.md)

