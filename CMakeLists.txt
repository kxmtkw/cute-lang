cmake_minimum_required(VERSION 3.12)
project(cutelang C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT BUILD)
    set(BUILD Release CACHE STRING "Choose debug or release" FORCE)
endif()

add_compile_options(-Wall -Wextra)

if(BUILD STREQUAL "debug")
    add_compile_options(-g)
    add_definitions(-DCT_CONF_DEBUG)
elseif(BUILD STREQUAL "release" OR BUILD STREQUAL "prod")
    add_compile_options(-O3)
endif()


add_executable(cute
	Engine/main/main.c
	Engine/core/core.c
	Engine/core/exec.c
	Engine/core/context.c
	Engine/image/image.c
	Engine/objects/object.c
	Engine/utils/utils.c
)

target_include_directories(cute PRIVATE Engine)
