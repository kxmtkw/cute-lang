from zero import *

C_STANDARD = Flags.gcc.std_c17

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


# Cute Engine

CuteRuntime = StaticLibrary()

src = Path("Runtime")
CuteRuntime.headers.public = src / "include"
CuteRuntime.headers.private = src

CuteRuntime.source = Source(
	src / "core" / "core.c",
	src / "core" / "exec.c",
	src / "core" / "context.c",

	src / "image" / "image.c",

	src / "objects" / "manager.c",
	src / "container" / "container.c",
	src / "utils" / "utils.c",

	src / "lib" / "buffer.c",
)

if DEBUG:
	CuteRuntime.arguments = Flags.Macro("CT_CONF_DEBUG"), C_STANDARD
else:
	CuteRuntime.arguments = C_STANDARD


# cute binary

cute = Executable()
cute.source = Source("main/runtime.c")
cute.link(CuteRuntime)