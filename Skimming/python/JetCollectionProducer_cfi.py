import FWCore.ParameterSet.Config as cms


karmaJets = cms.EDProducer(
    "JetCollectionProducer",
    cms.PSet(
        # take miniAOD AK4 jets by default
        inputCollection = cms.InputTag("slimmedJets"),

        # information to be filled into transient maps
        # it can then be accessed by other producers (e.g.
        # ValueMap producers)
        transientInformationSpec = cms.PSet(
            fromUserInt = cms.PSet(),
            fromUserIntAsBool = cms.PSet(),
            fromUserFloat = cms.PSet()
        ),

    )
)
