cmake_minimum_required(VERSION 3.12)
project(Cute C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_compile_options(-Wall -Wextra -g)

# --- Cute Instructions ---

add_library(CuteInstr STATIC
    Instr/image.c
)

target_include_directories(CuteInstr
    PUBLIC
        Instr/include
)

# --- Cute Runtime ---

add_library(CuteRuntime STATIC
    Runtime/core/core.c
    Runtime/core/exec.c
    Runtime/core/context.c
    Runtime/objects/manager.c
    Runtime/container/container.c
    Runtime/utils/utils.c
)

target_include_directories(CuteRuntime
    PUBLIC
        Runtime/include
    PRIVATE
        Runtime
)

target_link_libraries(CuteRuntime PUBLIC CuteInstr)

# --- cute binary ---

add_executable(cute main/runtime.c)
target_link_libraries(cute PRIVATE CuteRuntime)

# --- Cute Assembler ---

add_library(CuteAsm STATIC
    Assembler/tokenizer/tokenizer.cpp
    Assembler/tokenizer/stream.cpp
	Assembler/codegen/codegen.cpp
    Assembler/assembler/assembler.cpp
)

target_include_directories(CuteAsm
    PUBLIC
        Assembler/include
    PRIVATE
        Assembler
)

target_link_libraries(CuteAsm PUBLIC CuteInstr)

# --- cuteasm binary ---

add_executable(cuteasm main/assembler.cpp)
target_link_libraries(cuteasm PRIVATE CuteAsm)