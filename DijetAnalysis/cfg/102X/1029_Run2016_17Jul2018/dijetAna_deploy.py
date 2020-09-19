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

if __name__ == "__main__":

    for _jc in ("AK4PFCHS", "AK8PFCHS"):
        _deployer = KarmaAnalysisDeployerGC(
            nick="DijetAna_{}_JetHT_Run2016BCDEFGH-17Jul2018_2020-09-18".format(_jc),
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
        _deployer.add_constant("JET_COLLECTION", _jc)

        _deployer.add_lookup_parameter("JEC_VERSION", JEC_VERSION_LOOKUP, key="DATASETNICK")

        _deployer.deploy()
