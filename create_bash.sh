#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd) && cd ${SCRIPT_DIR}

EXOs=( "34" ) # "3" "4" "5" "7" "8" "9" "10" "12")

for EXO in "${EXOs[@]}"; do

	FC_FILENAME=${SCRIPT_DIR}/ex${EXO}.c

    #cp ${FC_FILENAME} ${FC_FILENAME}

    sed_triple=s:///://:g

    # def1
    machin="including ghosts & boundary constants"
    truc="including the number of ghost layers\n\/\/ for communications or boundary conditions"
    sed_param=s:${machin}:${truc}:g

    # def2
    machin2="double L=1.0;"
    truc2="double L=1.0;\n\/\/ definition of the source\n\/\/ the source corresponds to a disk of an uniform value\n\/\/ source1\: center=(0.4,0.4), radius=0.2 and value=100"
    sed_source1=s:${machin2}:${truc2}:g

    # def3
    machin3="double source2\[4\]={0.7, 0.8, 0.1, 200};"
    truc3="\/\/ source2\: center=(0.8,0.7), radius=0.1 and value=200\ndouble source2\[4\]={0.7, 0.8, 0.1, 200};\n\/\/ the order of the coordinates of the center (XX,YY) is inverted in the vector"
    sed_source2=s:${machin3}:${truc3}:g

    #def4: init
    machin4="Initialize the data all to 0 except for the left border (XX==0) initialized to 1 million"
    truc4="Initialize all the data to 0, with the exception of a given cell\n \*  whose center (cpos\_x,cpos\_y) is inside of the disks\n \*  defined by source1 or source2"
    sed_source4=s:${machin4}:${truc4}:g

    machin5="Exchanges ghost values with neighbours"
    truc5="Exchange ghost values with neighbours"
    sed_source5=s:${machin5}:${truc5}:g

    machin6="compute the local data-size with space for ghosts and boundary constants"
    truc6="compute the local data-size (the number of ghost layers is 2 for each coordinate)"
    sed_source6=s:${machin6}:${truc6}:g

    machin7="double cpos\_x,cpos\_y;"
    truc7="double cpos\_x,cpos\_y;\n\tdouble square_dist1, square_dist2;"
    sed_source7=s:${machin7}:${truc7}:g

    machin8="if((cpos\_y-source1\[0\])\*(cpos\_y-source1\[0\]) + (cpos\_x-source1\[1\])\*(cpos\_x-source1\[1\]) <= source1\[2\]\*source1\[2\])"
	truc8="square_dist1 = ( cpos\_y-source1\[0\] ) \* ( cpos\_y-source1\[0\] )\n\t\t\t\t     + ( cpos\_x-source1\[1\] ) \* ( cpos\_x-source1\[1\] );\n\t\t\tif (square_dist1 <= source1\[2\] \* source1\[2\])"
    sed_source8=s:${machin8}:${truc8}:g

    machin9="if((cpos\_y-source2\[0\])\*(cpos\_y-source2\[0\]) + (cpos\_x-source2\[1\])\*(cpos\_x-source2\[1\]) <= source2\[2\]\*source2\[2\])"
	truc9="square_dist2 = ( cpos\_y-source2\[0\] ) \* ( cpos\_y-source2\[0\] )\n\t\t\t\t     + ( cpos\_x-source2\[1\] ) \* ( cpos\_x-source2\[1\] );\n\t\t\tif (square_dist2 <= source2\[2\] \* source2\[2\])"
    sed_source9=s:${machin9}:${truc9}:g

    if [ "$EXO" -eq 3 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    elif [ "$EXO" -eq 4 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    elif [ "$EXO" -eq 5 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    else
        machin10="1, row, rank_dest,   100, \/\/ send column after ghost"
        truc10="1, row, rank_dest,   100, \/\/ send row after ghost"
        sed_source10=s:${machin10}:${truc10}:g

        machin12="1, row, rank_source, 100, \/\/ receive last column (ghost)"
        truc12="1, row, rank_source, 100, \/\/ receive last row (ghost)"
        sed_source12=s:${machin12}:${truc12}:g

        machin11=" 1, column, rank_dest,   100, \/\/ send column after ghost"
        truc11="          1, column, rank_dest,   100, \/\/ send column after ghost"
        sed_source11=s:${machin11}:${truc11}:g
    fi

    echo ${sed_param}
    sed -i "$sed_triple" ${FC_FILENAME}
    sed -i "$sed_param" ${FC_FILENAME}

    echo ${sed_source1}
    sed -i "$sed_source1" ${FC_FILENAME}

    echo ${sed_source2}
    sed -i "$sed_source2" ${FC_FILENAME}
    
    echo ${sed_source4}
    sed -i "$sed_source4" ${FC_FILENAME}

    echo ${sed_source5}
    sed -i "$sed_source5" ${FC_FILENAME}

    echo ${sed_source6}
    sed -i "$sed_source6" ${FC_FILENAME}

    echo ${sed_source7}
    sed -i "$sed_source7" ${FC_FILENAME}

    echo ${sed_source8}
    sed -i "$sed_source8" ${FC_FILENAME}

    echo ${sed_source9}
    sed -i "$sed_source9" ${FC_FILENAME}

    echo ${sed_source10}
    sed -i "$sed_source10" ${FC_FILENAME}

    echo ${sed_source12}
    sed -i "$sed_source12" ${FC_FILENAME}

    echo ${sed_source11}
    sed -i "$sed_source11" ${FC_FILENAME}
done

EXOs=( "6" ) #"5" "6" )

for EXO in "${EXOs[@]}"; do

	FC_FILENAME=${SCRIPT_DIR}/solutions/ex${EXO}.c

    #cp ${FC_FILENAME} ${FC_FILENAME}

    sed_triple=s:///://:g

    # def1
    machin="including ghosts & boundary constants"
    truc="including the number of ghost layers\n\/\/ for communications or boundary conditions"
    sed_param=s:${machin}:${truc}:g

    # def2
    machin2="double L=1.0;"
    truc2="double L=1.0;\n\/\/ definition of the source\n\/\/ the source corresponds to a disk of an uniform value\n\/\/ source1\: center=(0.4,0.4), radius=0.2 and value=100"
    sed_source1=s:${machin2}:${truc2}:g

    # def3
    machin3="double source2\[4\]={0.7, 0.8, 0.1, 200};"
    truc3="\/\/ source2\: center=(0.8,0.7), radius=0.1 and value=200\ndouble source2\[4\]={0.7, 0.8, 0.1, 200};\n\/\/ the order of the coordinates of the center (XX,YY) is inverted in the vector"
    sed_source2=s:${machin3}:${truc3}:g

    #def4: init
    machin4="Initialize the data all to 0 except for the left border (XX==0) initialized to 1 million"
    truc4="Initialize all the data to 0, with the exception of a given cell\n \*  whose center (cpos\_x,cpos\_y) is inside of the disks\n \*  defined by source1 or source2"
    sed_source4=s:${machin4}:${truc4}:g

    machin5="Exchanges ghost values with neighbours"
    truc5="Exchange ghost values with neighbours"
    sed_source5=s:${machin5}:${truc5}:g

    machin6="compute the local data-size with space for ghosts and boundary constants"
    truc6="compute the local data-size (the number of ghost layers is 2 for each coordinate)"
    sed_source6=s:${machin6}:${truc6}:g

    machin7="double cpos\_x,cpos\_y;"
    truc7="double cpos\_x,cpos\_y;\n\tdouble square_dist1, square_dist2;"
    sed_source7=s:${machin7}:${truc7}:g

    machin8="if((cpos\_y-source1\[0\])\*(cpos\_y-source1\[0\]) + (cpos\_x-source1\[1\])\*(cpos\_x-source1\[1\]) <= source1\[2\]\*source1\[2\])"
	truc8="square_dist1 = ( cpos\_y-source1\[0\] ) \* ( cpos\_y-source1\[0\] )\n\t\t\t\t     + ( cpos\_x-source1\[1\] ) \* ( cpos\_x-source1\[1\] );\n\t\t\tif (square_dist1 <= source1\[2\] \* source1\[2\])"
    sed_source8=s:${machin8}:${truc8}:g

    machin9="if((cpos\_y-source2\[0\])\*(cpos\_y-source2\[0\]) + (cpos\_x-source2\[1\])\*(cpos\_x-source2\[1\]) <= source2\[2\]\*source2\[2\])"
	truc9="square_dist2 = ( cpos\_y-source2\[0\] ) \* ( cpos\_y-source2\[0\] )\n\t\t\t\t     + ( cpos\_x-source2\[1\] ) \* ( cpos\_x-source2\[1\] );\n\t\t\tif (square_dist2 <= source2\[2\] \* source2\[2\])"
    sed_source9=s:${machin9}:${truc9}:g

    if [ "$EXO" -eq 3 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    elif [ "$EXO" -eq 4 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    elif [ "$EXO" -eq 5 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    elif [ "$EXO" -eq 6 ];then
        sed_source10=""
        sed_source11=""
        sed_source12=""
    else
        machin10="1, row, rank_dest,   100, \/\/ send column after ghost"
        truc10="1, row, rank_dest,   100, \/\/ send row after ghost"
        sed_source10=s:${machin10}:${truc10}:g

        machin12="1, row, rank_source, 100, \/\/ receive last column (ghost)"
        truc12="1, row, rank_source, 100, \/\/ receive last row (ghost)"
        sed_source12=s:${machin12}:${truc12}:g

        machin11=" 1, column, rank_dest,   100, \/\/ send column after ghost"
        truc11="          1, column, rank_dest,   100, \/\/ send column after ghost"
        sed_source11=s:${machin11}:${truc11}:g
    fi

    echo ${sed_param}
    sed -i "$sed_triple" ${FC_FILENAME}
    sed -i "$sed_param" ${FC_FILENAME}

    echo ${sed_source1}
    sed -i "$sed_source1" ${FC_FILENAME}

    echo ${sed_source2}
    sed -i "$sed_source2" ${FC_FILENAME}
    
    echo ${sed_source4}
    sed -i "$sed_source4" ${FC_FILENAME}

    echo ${sed_source5}
    sed -i "$sed_source5" ${FC_FILENAME}

    echo ${sed_source6}
    sed -i "$sed_source6" ${FC_FILENAME}

    echo ${sed_source7}
    sed -i "$sed_source7" ${FC_FILENAME}

    echo ${sed_source8}
    sed -i "$sed_source8" ${FC_FILENAME}

    echo ${sed_source9}
    sed -i "$sed_source9" ${FC_FILENAME}

    echo ${sed_source10}
    sed -i "$sed_source10" ${FC_FILENAME}

    echo ${sed_source12}
    sed -i "$sed_source12" ${FC_FILENAME}

    echo ${sed_source11}
    sed -i "$sed_source11" ${FC_FILENAME}
done