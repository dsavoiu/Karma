#!/usr/bin/env python
import os

from DijetAnalysis.Analysis.dijetAnalysisDeployers import DijetAnalysisDeployerGC


if __name__ == "__main__":

    #parser = ArgumentParser()
    #
    ## parser.add_argument()...
    #
    #args = parser.parse_args()

    _deployer = DijetAnalysisDeployerGC(
        nick="DijetAna_JetHT_Run2016G-Legacy-07Aug2017-v1_2018-09-20",
        cmsrun_config="dijetAna_cfg.py",
        gc_config_base="{}/src/DijetAnalysis/Analysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
        work_directory="_tmpwork"
    )

    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_JetHT_Run2016G-Legacy-07Aug2017-v1_2018-09-20/*.root")
    _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

    _deployer.add_constant("GLOBALTAG", "80X_dataRun2_2016LegacyRepro_v4")
    _deployer.add_constant("IS_DATA", "True")

    _deployer.deploy()
