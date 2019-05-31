#!/bin/sh
#
# Checkout script for Karma
###########################
#
# description:    skims suited for Dijet/Z+Jet analysis of 2016 data
# CMSSW version:  CMSSW_10_2_9
# created:        2019-05-23


_CMSSW_VERSION="CMSSW_10_2_9"
_CMSSW_SCRAM_SUFFIX=""

_CMSSW_DIR="${_CMSSW_VERSION}"
if [ "${_CMSSW_SCRAM_SUFFIX}" != "" ]; then
    _CMSSW_DIR="${_CMSSW_DIR}_${_CMSSW_SCRAM_SUFFIX}"
fi

# checkout workflow
# =================


# -- checks

# check for CMSSW
if [ -z "${CMS_PATH}" ]; then
    echo "[ERROR] Cannot find CMSSW: environment variable \$CMS_PATH is not set!"
    echo "[INFO] Have you done `source /cvmfs/cms.cern.ch/cmsset_default.sh`?"
fi

# -- initialization

# create a CMSSW working directory
echo "[INFO] Can create working area '${_CMSSW_DIR}'?"
if [ -d "${_CMSSW_DIR}" ]; then
    echo "[ERROR] Cannot create working area '${_CMSSW_DIR}': directory already exists!"
fi
scramv1 project -n "${_CMSSW_DIR}" CMSSW "${_CMSSW_VERSION}"

cd "${_CMSSW_DIR}/src"
eval `scramv1 runtime -sh`

# initialize git repository from CMSSW
git cms-init

# -- apply CMSSW modifications, backports, etc. (user code)
git cms-merge-topic knash:Winter16JetID_102X  # backport of TightLepVeto JetID

# -- get some modules directly from github

# Kappa
git clone https://github.com/dsavoiu/Karma.git $CMSSW_BASE/src/Karma

# Jet Toolbox
git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_102X


# -- compile using scram
scramv1 b -j20
