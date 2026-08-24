from zero import *

C_STANDARD = Flags.gcc.std_c17
CPP_STANDARD = Flags.gcc.std_cpp20

# Options

DEBUG = True if UserOptions.get("debug") == "true" else False

if DEBUG:
	print("Debug mode is on.") 

#  Configuration

build = Build()

build.compiler = "gcc"
build.directory = "build"
build.arguments = Flags.gcc.Wall, Flags.gcc.Wextra, Flags.gcc.g
build.export_compile_commands = True


# Cute Instructions

CuteInstr = StaticLibrary()
CuteInstr.source = Source(
	Path("Instr") / "image.c"
)
CuteInstr.headers.public = Path("Instr") / "include"
CuteInstr.arguments = C_STANDARD

# Cute Engine

CuteRuntime = StaticLibrary()

src = Path("Runtime")
CuteRuntime.headers.public = src / "include"
CuteRuntime.headers.private = src

CuteRuntime.source = Source(
	src / "core" / "core.c",
	src / "core" / "exec.c",
	src / "core" / "context.c",
	src / "objects" / "manager.c",
	src / "container" / "container.c",
	src / "utils" / "utils.c",

	src / "lib" / "buffer.c",
)

CuteRuntime.link(CuteInstr)

if DEBUG:
	CuteRuntime.arguments = Flags.Macro("CT_CONF_DEBUG"), C_STANDARD
else:
	CuteRuntime.arguments = C_STANDARD


# cute binary

cute = Executable()
cute.source = Source("main/runtime.c")
cute.link(CuteRuntime)


# Cute Assembler

CuteAsm = StaticLibrary()
CuteAsm.compiler = "g++"

src = Path("Assembler")

CuteAsm.headers.private = src
CuteAsm.headers.public = src / "include"
CuteAsm.source = Source(
	src / "tokenizer" / "tokenizer.cpp",
	src / "tokenizer" / "stream.cpp",
	src / "codegen" / "codegen.cpp",
	src / "assembler" / "assembler.cpp"
)

CuteAsm.arguments = CPP_STANDARD
CuteAsm.link(CuteInstr)


# cuteasm binary

cuteasm = Executable()
cuteasm.compiler = CuteAsm.compiler
cuteasm.source = Source("main/assembler.cpp")
cuteasm.link(CuteAsm)
