import FWCore.ParameterSet.Config as cms


# analyzer for writing out flat ntuple
zjetNtupleLeadingJetZBackToBackFilter = cms.EDFilter(
    "ZJetNtupleLeadingJetZBackToBackFilter",
    cms.PSet(
        maxDeltaPhi = cms.double(0.34),
    )
)
