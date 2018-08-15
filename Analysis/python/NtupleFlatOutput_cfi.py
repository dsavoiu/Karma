import FWCore.ParameterSet.Config as cms


# analyzer for writing out flat ntuple
dijetNtupleFlatOutput = cms.EDAnalyzer(
    "NtupleFlatOutput",
    cms.PSet(
        dijetNtupleSrc = cms.InputTag("ntuple"),
        outputFileName = cms.string("output_flat.root"),
        treeName = cms.string("Events"),
    )
)
