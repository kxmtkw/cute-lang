
# Building Cute

The required compiler is `gcc` or `clang`,

The project uses the `zero-build` build system (which I made myself :p). It is recommended you install that before building `Cute`. It's just a python package away.

Check out zero-build here: [zero-build](https://github.com/kxmtkw/ZeroBuild)


A `CMake` file is also exported with the project if you want to use that.

Both zero-build and cmake compile the same artifacts. Here is the dependency graph:
```
libCuteInstr.a
├── libCuteEngine.a
│	└── cute
└── libCuteAsm.a
	└── cuteasm
```

To build, first clone the repository and `cd` into the repo root.

### With ZeroBuild
Just run:
```bash
zero make
```
This will build inside `.build` directory. The executables can be found in `.build/bin`

### With CMake
First, create the build files:
```bash
cmake -B build 
```
Then build:
```bash
cmake --build build
```