#!/usr/bin/env bash

SPACK_DIR=/srv/storage/numpexexadi@storage2.grenoble.grid5000.fr/opt/spack
SPACK_ENV_DIR="spack_env"

if [ -d "$SPACK_ENV_DIR" ]; then
    echo "preparing spack environment "
    source $SPACK_DIR/share/spack/setup-env.sh
    spack -e $SPACK_ENV_DIR install -p16
    spack -e $SPACK_ENV_DIR find
else
    echo "Please source this file from the repository root."
fi
