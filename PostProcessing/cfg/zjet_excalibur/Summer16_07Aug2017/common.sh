#!/bin/bash

# -- sample-specific variables

# directory containing Excalibur TTree files
export SAMPLE_DIR="/portal/ekpbms3/home/tfesenbecker/excalibur_work/merged"
export SAMPLE_BASE_NAME="07Aug2017"
export SAMPLE_JECV_NAME="Summer16_JECV11"
export SAMPLE_NAME="${SAMPLE_BASE_NAME}_${SAMPLE_JECV_NAME}"

export SAMPLE_IOVS=`echo Run2016{BCD,EFearly,FlateGH}`
export SAMPLE_IOV_WHOLEYEAR="Run2016BCDEFGH"
