# theoutfit - ReXGlue Recompiled Project
#
# SDK boilerplate lives in generated/rexglue.cmake.

cmake_minimum_required(VERSION 3.25)
project(theoutfit LANGUAGES CXX RC)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(generated/rexglue.cmake)

# Sources
set(THEOUTFIT_SOURCES
    src/main.cpp
)

if(WIN32)
    list(APPEND THEOUTFIT_SOURCES src/theoutfit.rc)
endif()

if(WIN32)
    add_executable(theoutfit WIN32 ${THEOUTFIT_SOURCES})
else()
    add_executable(theoutfit ${THEOUTFIT_SOURCES})
endif()

rexglue_setup_target(theoutfit)
