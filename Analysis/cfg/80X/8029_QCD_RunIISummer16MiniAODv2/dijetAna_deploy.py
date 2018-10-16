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
        nick="DijetAna_QCD_RunIISummer16MiniAODv2_2018-09-30i_10fpj",
        cmsrun_config="dijetAna_cfg.py",
        gc_config_base="{}/src/DijetAnalysis/Analysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
        work_directory="_tmpwork",
        files_per_job=10,
    )

    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_15to30_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_30to50_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_50to80_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_80to120_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_120to170_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_170to300_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_300to470_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_470to600_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_600to800_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_800to1000_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_1000to1400_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_1400to1800_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_1800to2400_RunIISummer16MiniAODv2_2018-09-28/*.root")
    _deployer.add_input_files("/storage/gridka-nrg/dsavoiu/Dijet/test_skims/Dijet_QCD_Pt_2400to3200_RunIISummer16MiniAODv2_2018-09-28/*.root")

    _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

    _deployer.add_constant("GLOBALTAG", "80X_mcRun2_asymptotic_2016_TrancheIV_v6")
    _deployer.add_constant("IS_DATA", "False")

    _deployer.deploy()
