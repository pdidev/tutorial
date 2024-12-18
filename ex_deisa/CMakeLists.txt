set(CMAKE_C_STANDARD 99)

add_executable(simulation simulation.c)
target_link_libraries(simulation m MPI::MPI_C  paraconf::paraconf PDI::pdi)

