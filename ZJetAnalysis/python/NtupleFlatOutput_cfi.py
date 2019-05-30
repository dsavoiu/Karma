import FWCore.ParameterSet.Config as cms


# analyzer for writing out flat ntuple
zjetNtupleFlatOutput = cms.EDAnalyzer(
    "ZJetNtupleFlatOutput",
    cms.PSet(
        ntupleSrc = cms.InputTag("ntuple"),
        outputFileName = cms.string("output_flat.root"),
        treeName = cms.string("Events"),
        checkForCompleteness = cms.bool(True),
    )
)
