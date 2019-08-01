#!/bin/bash

# -- sample-specific variables

# directory containing Excalibur TTree files
export SAMPLE_DIR="/ceph/dsavoiu/JEC/Fall17/17Nov2017_V31_2018-10-26"
export SAMPLE_BASE_NAME="17Nov2017"
export SAMPLE_JECV_NAME="Fall17_JECV31"
export SAMPLE_NAME="${SAMPLE_BASE_NAME}_${SAMPLE_JECV_NAME}"

export SAMPLE_IOVS=`echo Run2017{B,C,DE,F}`
export SAMPLE_IOV_WHOLEYEAR="Run2017BCDEF"
