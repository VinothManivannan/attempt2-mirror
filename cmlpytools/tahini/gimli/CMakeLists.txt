cmake_minimum_required(VERSION 3.18.0)

set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)

project(gimli)

if(${CMAKE_SYSTEM_NAME} STREQUAL "Windows")

  find_package(LLVM REQUIRED CONFIG)

  add_executable(gimli gimli.cpp)

  target_compile_features(gimli PUBLIC cxx_std_17)
  target_link_libraries(gimli libLLVM-18)

  # Quick and dirty way of satisfying DLL dependencies - improve!!!
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libgcc_s_seh-1.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libLLVM-18.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libstdc++-6.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libwinpthread-1.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libffi-8.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libxml2-2.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/zlib1.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libiconv-2.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/liblzma-5.dll" $<TARGET_FILE_DIR:gimli>)
  add_custom_command(TARGET gimli POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different "$ENV{MSYS2_INSTALL_DIR}/mingw64/bin/libzstd.dll" $<TARGET_FILE_DIR:gimli>)

elseif(${CMAKE_SYSTEM_NAME} STREQUAL "Linux")

  find_package(ZLIB REQUIRED)
  find_package(LLVM REQUIRED CONFIG)

  add_executable(gimli gimli.cpp)

  target_include_directories(gimli PUBLIC /usr/lib/llvm-18/include)

  link_directories(/usr/lib/llvm-18/lib)

  target_compile_features(gimli PUBLIC cxx_std_17)
  target_link_libraries(gimli LLVMDebugInfoDWARF)

else()

  message(FATAL_ERROR "Use one of these options: -DCMAKE_SYSTEM_NAME=Windows|Linux")

endif()

add_subdirectory(test test)
