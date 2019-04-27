from Karma.Common.karmaPrelude_cff import *


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles = "file://{}/{}".format(os.getenv("CMSSW_BASE"), "src/Karma/Skimming/test/FullSkim/testFullSkim_out.root")
    options.isData = 1
    options.globalTag = "80X_dataRun2_2016LegacyRepro_v4"
    #options.edmOut="testFullAnalysis_out.root"
    options.maxEvents = 1000
    options.dumpPython = 1
    options.weightForStitching = 1.0
    options.jecVersion = "Summer16_07Aug2017GH_V11"
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
    options.weightForStitching = 1.0


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from Karma.DijetAnalysis.dijetAnalysis_cff import DijetAnalysis

# -- configure output ROOT file used by TFileService
process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("output.root"),
    closeFileFast = cms.untracked.bool(True),
)

ana = DijetAnalysis(process, is_data=options.isData, jec_version=options.jecVersion)

ana.configure()


# -- must be called at the end
finalizeAndRun(process, outputCommands=['drop *'])


## selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
