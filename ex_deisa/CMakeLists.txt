cmake_minimum_required(VERSION 3.9)

project(Deisa VERSION 1.0 LANGUAGES C CXX)

set(PDI_INSTALL_PATH "/gpfs/workdir/shared/pdi-deisa/spack/opt/spack/linux-centos7-cascadelake/gcc-11.2.0/pdi-1.6.0-ethkhjdusbqvy6zfc6egdue4ao65r3zx")

# Find MPI
find_package(MPI REQUIRED COMPONENTS CXX)
# Find the PDI library
find_library(PDI_LIBRARY NAMES pdi PATHS ${PDI_INSTALL_PATH}/lib)
# Find the Paraconf library
find_library(PARACONF_LIBRARY NAMES paraconf PATHS ${PDI_INSTALL_PATH}/lib)

# Include MPI headers
include_directories(${MPI_CXX_INCLUDE_PATH})
# Include PDI headers
include_directories(${PDI_INSTALL_PATH}/include)


# Add MPI copiler
add_definitions(${MPI_CXX_COMPILE_FLAGS})

add_executable(deisa main.c)
target_link_libraries(deisa ${MPI_CXX_LIBRARIES} ${MPI_CXX_LINK_FLAGS} ${PDI_LIBRARY} ${PARACONF_LIBRARY})
set_target_properties(deisa PROPERTIES ENABLE_EXPORTS TRUE)
