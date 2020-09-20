import os

import FWCore.ParameterSet.Config as cms

from Karma.DijetAnalysis.Configuration import dijetAnalysis_94X_Run2016_17Jul2018_cff
from Karma.Common.Tools import KarmaOptions, KarmaProcess


# set up and parse command-line options
if not os.getenv("GC_VERSION"):
    # -- *not* running in grid -> simple test
    options = (
        dijetAnalysis_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
            #.setDefault('inputFiles', "root://cmsxrootd-redirectors.gridka.de//store/user/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016G-17Jul2018-v1_2019-05-25/job_2061_output.root")
            #.setDefault('inputFiles', "root://cmsxrootd-redirectors.gridka.de//store/user/dsavoiu/Dijet/skims/KarmaSkim_JetHT_Run2016G-17Jul2018-v1_2020-01-09/job_3029_output.root")
            #.setDefault('inputFiles', "file:///portal/ekpbms3/home/dsavoiu/Dijet/CMSSW_10_2_18/src/Karma/Skimming/cfg/102X/1029_DijetSkim_JetHT_Run2016_17Jul2018/testFullSkim_out_10000events.root")
            #.setDefault('inputFiles', "file:///portal/ekpbms3/home/dsavoiu/Dijet/CMSSW_10_2_18/src/Karma/Skimming/cfg/102X/1029_DijetSkim_JetHT_Run2016_17Jul2018/testFullSkim_out_12events.root")
            .setDefault('inputFiles', "file:///portal/ekpbms3/home/dsavoiu/Dijet/CMSSW_10_2_18/src/Karma/Skimming/cfg/102X/1029_DijetSkim_JetHT_Run2016_17Jul2018/testFullSkim_out_100events.root")           
            .setDefault('outputFile', "testFullAnalysis_out_100events.root")
            .setDefault('maxEvents', 100)
            #.setDefault('outputFile', "testFullAnalysis_out.root")
            #.setDefault('maxEvents', -1)
            .setDefault('isData', True)
            .setDefault('globalTag', "94X_dataRun2_v10")
            #.setDefault('jsonFilterFile', os.path.realpath("{}/src/Karma/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE"))))
            .setDefault('dumpPython', True)
            .setDefault('useHLTFilter', False)
            .setDefault('useObjectBasedJetID', True)
            .setDefault('jetCollections', ['AK4PFCHS', 'AK8PFCHS'])
            .setDefault('jetIDSpec', "2016")
            .setDefault('jetIDWorkingPoint', "TightLepVeto")
            .setDefault('numThreads', 1)
            .setDefault('jecVersion', "Summer16_07Aug2017GH_V11")  # for JEC uncertainty sources
            .setDefault('jecFromGlobalTag', True)
            .setDefault('doJECUncertaintySources', True)
            .setDefault('doPrescales', True)
            .setDefault('edmOut', True)
    ).parseArguments()
else:
    # -- running on grid node -> "production" config
    options = (
        dijetAnalysis_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
            .setDefault('inputFiles', [__FILE_NAMES__])
            .setDefault('outputFile', "output.root")
            .setDefault('isData', __IS_DATA__)
            .setDefault('jsonFilterFile', os.path.realpath("{}/src/Karma/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE"))))
            .setDefault('globalTag', "__GLOBALTAG__")
            .setDefault('maxEvents', -1)
            .setDefault('dumpPython', False)
            .setDefault('reportEvery', 10000)
            .setDefault('numThreads', 1)
            .setDefault('useHLTFilter', True)
            .setDefault('useObjectBasedJetID', True)
            .setDefault('jetCollections', [__JET_COLLECTION__])
            .setDefault('jetIDSpec', "2016")
            .setDefault('jetIDWorkingPoint', "TightLepVeto")
            #.setDefault('jecVersion', "__JEC_VERSION__")
            .setDefault('jecFromGlobalTag', True)
            .setDefault('doJECUncertaintySources', True)
            .setDefault('doPrescales', True)
            .setDefault('edmOut', False)
    ).parseArguments()


# create the process
process = KarmaProcess(
    "DIJETANA",
    input_files=options.inputFiles,
    max_events=options.maxEvents,
    global_tag=options.globalTag,
    edm_out='.'.join(options.outputFile.split('.')[:-1]) + "_edmOut.root" if options.edmOut else None,
    num_threads=options.numThreads,
)

from PhysicsTools.PatUtils.l1ECALPrefiringWeightProducer_cfi import l1ECALPrefiringWeightProducer
process.prefiringweight = l1ECALPrefiringWeightProducer.clone(
    DataEra = cms.string("2016BtoH"),
    UseJetEMPt = cms.bool(False),
    PrefiringRateSystematicUncty = cms.double(0.2),
    SkipWarnings = False)

print(process.paths) #[0] += process.prefiringweight

process.enable_verbose_logging()  # for testing

# configure the process
dijetAnalysis_94X_Run2016_17Jul2018_cff.configure(process, options)

# dump expanded cmsRun configuration
if options.dumpPython:
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# print out configuration before running
process.print_configuration()
