#!/bin/bash

 SYNTAGRUSDIR=$1
 TEMPDIR=$2
 OUTDIR=$3
 echo "export OMP_NUM_THREADS=8"
 python2.7 syntagrus2malt.py $SYNTAGRUSDIR $TEMPDIR ruscorpora_syntagrus $OUTDIR
 python2.7 auto_run_xml.py $OUTDIR
