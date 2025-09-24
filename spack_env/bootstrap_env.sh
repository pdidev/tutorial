#!/usr/bin/env bash

SPACK_DIR=/srv/storage/numpexexadi@storage2.grenoble.grid5000.fr/opt/spack
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $SPACK_DIR/share/spack/setup-env.sh
cd $SCRIPT_DIR/..
spack env activate spack_env
spack install -p16
spack find
