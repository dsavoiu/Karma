#!/usr/bin/env python
import os

from Karma.Common.Tools.karmaAnalysisDeployers import KarmaAnalysisDeployerGC


DATASETS = {
    "ZJetsToNuNu" : dict(
        CROSS_SECTION_LOOKUP = {
            "ZJetsToNuNu_Zpt-100to200" : 35.99    ,
            "ZJetsToNuNu_Zpt-200toInf" : 4.201    ,
        },
        NUMBER_OF_EVENTS_LOOKUP = {
            "ZJetsToNuNu_Zpt-100to200" : 5077952  ,
            "ZJetsToNuNu_Zpt-200toInf" : 1986102  ,
        },
    ),
    "WJetsToLNu" : dict(
        CROSS_SECTION_LOOKUP = {
            "WJetsToLNu"               : 50260.0  ,
        },
        NUMBER_OF_EVENTS_LOOKUP = {
            "WJetsToLNu"               : 29514020 ,
        },
    ),
    "TTJets" : dict(
        CROSS_SECTION_LOOKUP = {
            "TTJets"                   : 511.3    ,
        },
        NUMBER_OF_EVENTS_LOOKUP = {
            "TTJets"                   : 10199051 ,
        },
    ),
}


if __name__ == "__main__":


    _skim_date = "2019-07-03"
    for _dataset_name, _dataset_conf in DATASETS.iteritems():

        _deployer = KarmaAnalysisDeployerGC(
            nick="DijetAna_{}_RunIISummer16MiniAODv3_2020-01-23".format(_dataset_name),
            cmsrun_config="dijetAna_cfg.py",
            gc_config_base="{}/src/Karma/DijetAnalysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
            work_directory="/portal/ekpbms3/home/{}/work/dijet_ana".format(os.getenv("USER")),
            files_per_job=5,
        )

        for _sample in _dataset_conf['CROSS_SECTION_LOOKUP'].keys():
            _deployer.add_input_files(_sample, "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_{}_RunIISummer16MiniAODv3_{}/*.root".format(_sample, _skim_date))

        _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

        _deployer.add_constant("GLOBALTAG", "94X_mcRun2_asymptotic_v3")
        _deployer.add_constant("IS_DATA", "False")
        _deployer.add_constant("JEC_VERSION", "Summer16_07Aug2017_V11")
        _deployer.add_constant("JER_VERSION", "Summer16_25nsV1")

        _deployer.add_lookup_parameter("CROSS_SECTION", _dataset_conf['CROSS_SECTION_LOOKUP'], key="DATASETNICK")
        _deployer.add_lookup_parameter("NUMBER_OF_EVENTS", _dataset_conf['NUMBER_OF_EVENTS_LOOKUP'], key="DATASETNICK")

        _deployer.deploy()
