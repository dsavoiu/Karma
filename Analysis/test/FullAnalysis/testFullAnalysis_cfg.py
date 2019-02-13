from DijetAnalysis.Core.dijetPrelude_cff import *


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../../Skimming/test/FullSkim/testFullSkim_out.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
#options.edmOut="testFullAnalysis_out.root"  # no EDM output
options.maxEvents=-1 #10 #000
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


from DijetAnalysis.Analysis.dijetAnalysis_cff import DijetAnalysis

# -- configure output ROOT file used by TFileService
process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("output.root"),
    closeFileFast = cms.untracked.bool(True),
)

ana = DijetAnalysis(process, is_data=options.isData)

ana.configure()


# -- must be called at the end
finalizeAndRun(process, outputCommands=['drop *'])


## selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
