cmake_minimum_required(VERSION 3.12)
project(Cute C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_compile_options(-Wall -Wextra -g)

add_executable(cute
	Engine/main/main.c
	Engine/core/core.c
	Engine/core/exec.c
	Engine/core/context.c
	Engine/image/image.c
	Engine/objects/manager.c
	Engine/container/container.c
	Engine/utils/utils.c
	Engine/lib/buffer.c
)

target_include_directories(cute PRIVATE Engine)
