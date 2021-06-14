#!/usr/bin/env python
import os

from Karma.Common.Tools.karmaAnalysisDeployers import KarmaAnalysisDeployerGC


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
PREFIRING_WEIGHT_HIST_NAME_LOOKUP = {
    "JetHT_Run2016B_ver1"  : "L1prefiring_jetpt_2016BCD",
    "JetHT_Run2016B_ver2"  : "L1prefiring_jetpt_2016BCD",
    "JetHT_Run2016C"       : "L1prefiring_jetpt_2016BCD",
    "JetHT_Run2016D"       : "L1prefiring_jetpt_2016BCD",
    "JetHT_Run2016E"       : "L1prefiring_jetpt_2016EF",
    "JetHT_Run2016F"       : "L1prefiring_jetpt_2016EF",
    "JetHT_Run2016G"       : "L1prefiring_jetpt_2016FGH",
    "JetHT_Run2016H"       : "L1prefiring_jetpt_2016FGH",
}

if __name__ == "__main__":

    _deployer = KarmaAnalysisDeployerGC(
        nick="DijetAna_JetHT_Run2016BCDEFGH-17Jul2018_2021-06-14_prefiringByIOV_ntupleV2",
        cmsrun_config="dijetAna_cfg.py",
        gc_config_base="{}/src/Karma/DijetAnalysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
        work_directory="/work/{}/Dijet/.workdirs/dijet_ana".format(os.getenv("USER")),
        files_per_job=10,
    )

    _skim_date = "2020-09-15"
    _deployer.add_input_files("JetHT_Run2016B_ver1", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016B-17Jul2018_ver1-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016B_ver2", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016B-17Jul2018_ver2-v2_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016C",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016C-17Jul2018-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016D",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016D-17Jul2018-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016E",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016E-17Jul2018-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016F",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016F-17Jul2018-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016G",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016G-17Jul2018-v1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("JetHT_Run2016H",      "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016H-17Jul2018-v1_{}/*.root".format(_skim_date))

    _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

    _deployer.add_constant("GLOBALTAG", "94X_dataRun2_v10")
    _deployer.add_constant("IS_DATA", "True")

    _deployer.add_lookup_parameter("JEC_VERSION", JEC_VERSION_LOOKUP, key="DATASETNICK")
    _deployer.add_lookup_parameter("PREFIRING_WEIGHT_HIST_NAME", PREFIRING_WEIGHT_HIST_NAME_LOOKUP, key="DATASETNICK")

    _deployer.deploy()
