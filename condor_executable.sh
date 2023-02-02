#!/bin/bash

# export EOS_MGM_URL=root://eosuser.cern.ch

source /usr/local/xsuite/miniforge3/bin/activate xsuite
pwd

cp -r /afs/cern.ch/work/f/fasvesta/benchmarking_psb/PSB .
cp /afs/cern.ch/work/f/fasvesta/benchmarking_psb/*.py .
mkdir output

python examplePSBPIC.py 524
mkdir /eos/user/f/fasvesta/benchmarking_psb/output_524
xrdcp output/* root://eosuser.cern.ch//eos/user/f/fasvesta/benchmarking_psb/output_524/.
