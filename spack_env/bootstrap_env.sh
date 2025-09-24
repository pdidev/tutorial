#!/usr/bin/env bash

SPACK_DIR=/srv/storage/numpexexadi@storage2.grenoble.grid5000.fr/opt/spack
SPACK_ENV_DIR="spack_env"

if [ -d "$SPACK_ENV_DIR" ]; then
    source $SPACK_DIR/share/spack/setup-env.sh
    spack env activate $SPACK_ENV_DIR
    spack install -p16
    spack find
fi
