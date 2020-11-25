#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Illegal number of arguments. Please pass correct ex number."
    exit 1
fi
docker run -v $(pwd):/home/default/tutorial pdidevel/xenial_pdi /bin/bash -c "cmake tutorial > /dev/null && make $1 > /dev/null && cp tutorial/$1.yml . && ./$1"
