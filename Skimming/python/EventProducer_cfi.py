import FWCore.ParameterSet.Config as cms


dijetEventProducer = cms.EDProducer(
    "EventProducer",
    cms.PSet(
        hltProcessName = cms.string("HLT"),
        hltPrescaleProvider = cms.PSet(
            l1GtRecordInputTag = cms.InputTag("l1GtTriggerMenuLite"),
            l1GtReadoutRecordInputTag = cms.InputTag(""),
            l1GtTriggerMenuLiteInputTag =  cms.InputTag("l1GtTriggerMenuLite"),
        ),
        hltRegexes = cms.vstring("HLT_PFJet[0-9]+_v[0-9]+"),
        hltFilterRegexes = cms.vstring("^hltSinglePFJet[0-9]+$"),
        #hltL1FilterRegexes = cms.vstring("^hltL1sSingleJet.*"),
    )
)
