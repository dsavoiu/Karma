from DijetAnalysis.Core.dijetPrelude_cff import *


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles = "file://{}".format(os.path.realpath("../../../../../../Skimming/test/FullMCSkim/testFullMCSkim_out.root"))
    options.isData = 0
    options.globalTag = "80X_mcRun2_asymptotic_2016_TrancheIV_v6"
    #options.edmOut="testFullAnalysis_out.root"
    options.maxEvents = 1000
    options.dumpPython = 1
    options.weightForStitching = 1.0
    options.jecVersion = "Summer16_07Aug2017_V11"
else:
    # -- running on grid node
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    #options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
    options.dumpPython = False
    options.reportEvery = 100000 #int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]
    options.jecVersion = "__JEC_VERSION__"
    options.weightForStitching = float(__CROSS_SECTION__) / float(__NUMBER_OF_EVENTS__)


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from DijetAnalysis.Analysis.dijetAnalysis_cff import DijetAnalysis

# -- configure output ROOT file used by TFileService
process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("output.root"),
    closeFileFast = cms.untracked.bool(True),
)

ana = DijetAnalysis(process, is_data=options.isData, jec_version=options.jecVersion, weight_for_stitching=options.weightForStitching)

ana.configure()


# -- must be called at the end
finalizeAndRun(process, outputCommands=['drop *'])


## selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
