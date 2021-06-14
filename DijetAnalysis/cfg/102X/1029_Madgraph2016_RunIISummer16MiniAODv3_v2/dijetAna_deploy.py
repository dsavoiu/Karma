#!/usr/bin/env python
import os

from Karma.Common.Tools.karmaAnalysisDeployers import KarmaAnalysisDeployerGC


CROSS_SECTION_LOOKUP = {
    "QCD_HT50to100":    2.464e+08,
    "QCD_HT100to200":   2.794e+07,
    "QCD_HT200to300":   1.712e+06,
    "QCD_HT300to500":   347700,
    "QCD_HT500to700":   32150,
    "QCD_HT700to1000":  6837,
    "QCD_HT1000to1500": 1208,
    "QCD_HT1500to2000": 120,
    "QCD_HT2000toInf":  25.3,
}

NUMBER_OF_EVENTS_LOOKUP = {
    "QCD_HT50to100":    4180469,
    "QCD_HT100to200":   82293477,
    # second term refers to extended sample
    "QCD_HT200to300":   18722416 + 38857977,
    "QCD_HT300to500":   17035891 + 37516961,
    "QCD_HT500to700":   18560541 + 44061488,
    "QCD_HT700to1000":  15629253 + 21604533,
    "QCD_HT1000to1500": 4850746  + 10360193,
    "QCD_HT1500to2000": 3970819  + 7868538,
    "QCD_HT2000toInf":  1991645  + 4027896,
}

if __name__ == "__main__":

    _deployer = KarmaAnalysisDeployerGC(
        nick="DijetAna_Madgraph2016_RunIISummer16MiniAODv3_2021-06-14_hybridJER_ntupleV2",
        cmsrun_config="dijetAna_cfg.py",
        gc_config_base="{}/src/Karma/DijetAnalysis/cfg/gc/dijetAna_base_gc.conf".format(os.getenv("CMSSW_BASE")),
        work_directory="/work/{}/Dijet/.workdirs/dijet_ana".format(os.getenv("USER")),
        files_per_job=5,
    )

    _skim_date = "2020-09-15"
    _deployer.add_input_files("QCD_HT50to100",    "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT50to100_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT100to200",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT100to200_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT200to300",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT200to300_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT300to500",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT300to500_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT500to700",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT500to700_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT700to1000",  "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT700to1000_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT1000to1500", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT1000to1500_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT1500to2000", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT1500to2000_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT2000toInf",  "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT2000toInf_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_{}/*.root".format(_skim_date))
    
    # extended MC samples
    _deployer.add_input_files("QCD_HT200to300",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT200to300_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT300to500",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT300to500_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT500to700",   "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT500to700_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT700to1000",  "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT700to1000_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT1000to1500", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT1000to1500_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT1500to2000", "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT1500to2000_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))
    _deployer.add_input_files("QCD_HT2000toInf",  "/storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT2000toInf_madgraphMLM-pythia8_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1_{}/*.root".format(_skim_date))

    _deployer.replace_file_prefix('/storage/gridka-nrg/', 'root://cmsxrootd-1.gridka.de:1094//store/user/')

    _deployer.add_constant("GLOBALTAG", "94X_mcRun2_asymptotic_v3")
    _deployer.add_constant("IS_DATA", "False")
    _deployer.add_constant("JEC_VERSION", "Summer16_07Aug2017_V11")
    _deployer.add_constant("JER_VERSION", "Summer16_25nsV1")

    _deployer.add_lookup_parameter("CROSS_SECTION", CROSS_SECTION_LOOKUP, key="DATASETNICK")
    _deployer.add_lookup_parameter("NUMBER_OF_EVENTS", NUMBER_OF_EVENTS_LOOKUP, key="DATASETNICK")

    _deployer.deploy()
