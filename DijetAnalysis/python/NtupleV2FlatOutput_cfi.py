import FWCore.ParameterSet.Config as cms


# analyzer for writing out flat ntuple
dijetNtupleV2FlatOutput = cms.EDAnalyzer(
    "DijetNtupleV2FlatOutput",
    cms.PSet(
        ntupleSrc = cms.InputTag("ntuple"),
        outputFileName = cms.string("output_flat.root"),
        treeName = cms.string("Events"),
        checkForCompleteness = cms.bool(True),
    )
)
