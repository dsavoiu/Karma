#!/usr/bin/env python
import os

from Karma.Common.Tools.karmaAnalysisDeployers import KarmaAnalysisDeployerGC


CROSS_SECTION_LOOKUP = {
    "QCD_Flat_Pt_15to7000" : 1972000000,  # 1.972e+09 pb
}

NUMBER_OF_EVENTS_LOOKUP = {
    "QCD_Flat_Pt_15to7000" : 9951232,
}

if __name__ == "__main__":

    _deployer = KarmaAnalysisDeployerGC(
        nick="DijetAna_Pythia2016_Flat_RunIISummer16MiniAODv3_2022-01-20_ntupleV2",
        cmsrun_config="dijetAna_cfg.py",
        gc_config_base="{}/src/Karma/DijetAnalysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
        work_directory="/work/{}/Dijet/.workdirs/dijet_ana".format(os.getenv("USER")),
        files_per_job=5,
    )

    _skim_date = "2022-01-20"
    _deployer.add_input_files("QCD_Flat_Pt_15to7000", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_Flat_Pt_15to7000_RunIISummer16MiniAODv3_{}/*.root".format(_skim_date))

    _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

    _deployer.add_constant("GLOBALTAG", "94X_mcRun2_asymptotic_v3")
    _deployer.add_constant("IS_DATA", "False")
    _deployer.add_constant("JEC_VERSION", "Summer16_07Aug2017_V11")
    _deployer.add_constant("JER_VERSION", "Summer16_25nsV1")

    _deployer.add_lookup_parameter("CROSS_SECTION", CROSS_SECTION_LOOKUP, key="DATASETNICK")
    _deployer.add_lookup_parameter("NUMBER_OF_EVENTS", NUMBER_OF_EVENTS_LOOKUP, key="DATASETNICK")

    _deployer.deploy()
