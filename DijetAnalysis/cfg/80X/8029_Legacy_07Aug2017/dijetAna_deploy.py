#!/usr/bin/env python
import os

from Karma.DijetAnalysis.dijetAnalysisDeployers import DijetAnalysisDeployerGC


JEC_VERSION_LOOKUP = {
    "JetHT_Run2016B_ver1"  : "Summer16_07Aug2017BCD_V11",
    "JetHT_Run2016B_ver2"  : "Summer16_07Aug2017BCD_V11",
    "JetHT_Run2016C"       : "Summer16_07Aug2017BCD_V11",
    "JetHT_Run2016D"       : "Summer16_07Aug2017BCD_V11",
    "JetHT_Run2016E"       : "Summer16_07Aug2017EF_V11",
    "JetHT_Run2016F"       : "Summer16_07Aug2017EF_V11",
    "JetHT_Run2016G"       : "Summer16_07Aug2017GH_V11",
    "JetHT_Run2016H"       : "Summer16_07Aug2017GH_V11",
}

if __name__ == "__main__":

    _deployer = DijetAnalysisDeployerGC(
        nick="DijetAna_JetHT_Run2016BCDEFGH-Legacy-07Aug2017-v1_2019-03-18",
        cmsrun_config="dijetAna_cfg.py",
        gc_config_base="{}/src/Karma/DijetAnalysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
        work_directory="/home/{}/work/dijet_ana".format(os.getenv("USER")),
        files_per_job=10,
    )

    _skim_date = "2019-03-14"
    _deployer.add_input_files("JetHT_Run2016B_ver1", "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016B-Legacy-07Aug2017_ver1-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016B_ver2", "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016B-Legacy-07Aug2017_ver2-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016C",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016C-Legacy-07Aug2017-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016D",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016D-Legacy-07Aug2017-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016E",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016E-Legacy-07Aug2017-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016F",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016F-Legacy-07Aug2017-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016G",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016G-Legacy-07Aug2017-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016H",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/Dijet_JetHT_Run2016H-Legacy-07Aug2017-v1_{}/*.root".format(_skim_date))

    _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

    _deployer.add_constant("GLOBALTAG", "80X_dataRun2_2016LegacyRepro_v4")
    _deployer.add_constant("IS_DATA", "True")

    _deployer.add_lookup_parameter("JEC_VERSION", JEC_VERSION_LOOKUP, key="DATASETNICK")

    _deployer.deploy()
