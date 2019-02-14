import FWCore.ParameterSet.Config as cms


def dijetEventProducer(isData):
    """create the producer for CHS MET, adding necessary prerequisites to the process"""

    return cms.EDProducer(
        "EventProducer",
        cms.PSet(
            # -- input sources
            pileupDensitySrc = cms.InputTag("fixedGridRhoFastjetAll"),
            pileupSummaryInfoSrc = cms.InputTag("slimmedAddPileupInfo"),
            triggerResultsSrc = cms.InputTag("TriggerResults", "", "HLT"),
            #triggerPrescalesSrc = cms.InputTag("patTrigger"),
            primaryVerticesSrc = cms.InputTag("offlineSlimmedPrimaryVertices"),
            goodPrimaryVerticesSrc = cms.InputTag("goodOfflinePrimaryVertices"),

            # -- other configuration
            isData = cms.bool(isData),

            # name of the HLT process (for HLTConfigProvider)
            hltProcessName = cms.string("HLT"),

            # HLTPrescaleProvider configuration
            hltPrescaleProvider = cms.PSet(
                l1GtRecordInputTag = cms.InputTag("l1GtTriggerMenuLite"),
                l1GtReadoutRecordInputTag = cms.InputTag(""),
                l1GtTriggerMenuLiteInputTag =  cms.InputTag("l1GtTriggerMenuLite"),
            ),

            # interesting trigger paths must match one of these regexes:
            hltRegexes = cms.vstring("HLT_(AK8)?PFJet[0-9]+_v[0-9]+", "HLT_DiPFJetAve[0-9]+_v[0-9]+"),
        )
    )
