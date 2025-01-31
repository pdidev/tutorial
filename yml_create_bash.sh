#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd) && cd ${SCRIPT_DIR}


EXOs=( "3" "4" "5" "7" "8" "9" "10" "12" )

#EXOs=( "7" ) # "4" "5" "7" "8" "9" "10" "12")

for EXO in "${EXOs[@]}"; do

	FC_FILENAME=${SCRIPT_DIR}/ex${EXO}.yml
    #cp ${FC_FILENAME} ${FC_FILENAME}


    machin12="excluding spacer for boundary conditions or ghosts"
    truc12="excluding the number of ghost layers for boundary conditions"
    sed_source12=s:${machin12}:${truc12}:g

    echo ${sed_source12}
    sed -i "$sed_source12" ${FC_FILENAME}    



done

for EXO in "${EXOs[@]}"; do

	FC_FILENAME=${SCRIPT_DIR}/solutions/ex${EXO}.yml
    #cp ${FC_FILENAME} ${FC_FILENAME}

    machin12="excluding spacer for boundary conditions or ghosts"
    truc12="excluding the number of ghost layers for boundary conditions"
    sed_source12=s:${machin12}:${truc12}:g

    echo ${sed_source12}
    sed -i "$sed_source12" ${FC_FILENAME}    
done