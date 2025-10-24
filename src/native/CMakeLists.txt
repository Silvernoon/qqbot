cmake_minimum_required(VERSION 3.15)
project(native VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 REQUIRED)

pybind11_add_module(openai_native src/chat.cpp src/pybind.cpp)

#target_compile_options(native PRIVATE -O3 -Wall)

target_include_directories(openai_native PRIVATE
    ${Python_INCLUDE_DIRS}
)

target_link_libraries(openai_native PRIVATE
    pybind11::headers
    pybind11::module
    ${Python_LIBRARIES}
)

# 设置输出目录
#set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/dist)

set_target_properties(openai_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/..
)
