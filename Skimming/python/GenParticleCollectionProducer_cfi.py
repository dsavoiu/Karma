import FWCore.ParameterSet.Config as cms


karmaGenParticleCollectionProducer = cms.EDProducer(
    "GenParticleCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("prunedGenParticles"),
        allowedPDGIds = cms.vint32(
             1,  2,  3,  4,  5,  6,  9,  11,  12,  13,  14,  15,  16,  21,  22,  23,  24,
            -1, -2, -3, -4, -5, -6,     -11, -12, -13, -14, -15, -16,                -24
        ),
    )
)
