## TODO

A list of stuff to do.


### Language & Compiler

- Implement functions in the the language
- Add `__builtin__` to the language.
```
__builtin__ out int x

// Parsing is simple, just simple tokens parsed into a "Builtin" node
// name resolver and type checker ignore this
// codegen is the one that actually parses it

__builtin__ modcall io print x
__builtin__ halt 0
__builtin__ out int 10

// Could also allow instructions ngl

__builtin__ addi x y z
```

- Add name resolution with scoping (no closures).
- Add type checking.
- Add containers.
- Add virtual containers or box.
	- It would be preferred that this is used to represent the primitive types.	
	- That would allow the type checker to purely be container based.
	Here is we can implement that:
```
virtual container int(atom)

inline func int.#add(other: int) {
	let res: int
	__builtin__ addi res this other
	return res
}

func main() {
	x = 12 + 12 ->
	x = 12.#add(12)
	x = {
		let res: int
		__builtin__ addi res this other
		res
	}
}
```
- What this snippet requires us to do:
	- Function inlining is just substituting blocks.
	- Block is an expression who's last value is the expression result.
	- `#` indicates special methods.
	- The compiler will not have to manually map types to instructions.
		- This might bite us back later tho.


### Runtime

- Add an IO module.
- Allow buffer module to load bytes from the data section.