import FWCore.ParameterSet.Config as cms


dijetNtupleV2Splicer = cms.EDFilter(
    "NtupleV2Splicer",
    cms.PSet(
        # -- input sources
        dijetNtupleV2Src = cms.InputTag("ntuple"),

        # -- other configuration
        spliceName = cms.string("ys01yb01"),
        spliceFilterExpression = cms.string("0<abs(jet12yboost)<=1&&0<abs(jet12ystar)<=1"),

        #splices = cms.PSet(
        #    ys01yb01 = cms.PSet(
        #        yBoostBin = cms.vdouble(0, 1),
        #        yStarBin = cms.vdouble(0, 1),
        #    )
        #)
    )
)
