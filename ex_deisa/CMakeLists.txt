set(CMAKE_C_STANDARD 99)

add_executable(deisa main.c)
target_link_libraries(deisa m MPI::MPI_C paraconf::paraconf PDI::pdi)
set_target_properties(deisa PROPERTIES ENABLE_EXPORTS TRUE)