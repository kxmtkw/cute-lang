
# Architecture

### Overview

`Cute` is a 64-bit register-based virtual machine toolchain consisting of two primary binaries:

1. `cuteasm`: Compiles `.csm` assembly text files into `.cute` executable images.
2. `cute`: The runtime that loads and executes `.cute` images.


### Toolchain Pipeline
```
Source Code (.ct)
		|
	    v
┌────────────────────┐
│    Cute Compiler   │  (Compiling code file/s to a single image file)
└────────────────────┘
		|
		v
Executable Image (.cute)
		|
		v
┌────────────────────┐
│    Cute Runtime    │  (Executing image file)
└────────────────────┘
```

### Project Structure
``` bash
.
├── Compiler # Main Cute Compiler
│   ├── lexer  # converts source code into lexemes 
│   ├── parser # parses tokens to construct an ast
│   ├── resolver # name resolution and operation resolution
│   ├── codegen # converting AST to bytecode
│   └── defs # common definitions required by the compiler
│
├── Runtime # Main Engine Source Code
│   ├── common # common headers needed throughout the engine
│   ├── container # sub class of object, exposed to the asm
│   ├── core # heart of the runtime
│   ├── include # public header including the engine defs and instruction set
│   ├── modules # module system for extended functionality
│   ├── objects # objects subsystem, gc, object defintions and manager
│   └── utils # small utils needed in the engine
│
├── main # Main binary entry point: cute
│
├── dev # Place for testing
│
├── editor # tooling for editors
│
└── docs # Documentation
    └── records # list of recorded design choices
```

### Building

It is required that you build the engine using either `gcc` or `clang`.
The build system recommended is `ZeroBuild`.
See more on how to build [here](07-building.md).