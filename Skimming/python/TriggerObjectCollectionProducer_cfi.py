import FWCore.ParameterSet.Config as cms

from Karma.Common.util import CMSSW_VERSION


TRIGGER_MODULE_NAME = 'selectedPatTrigger'
if CMSSW_VERSION >= (9,2,1):
    TRIGGER_MODULE_NAME = 'slimmedPatTrigger'

karmaTriggerObjectCollectionProducer = cms.EDProducer(
    "TriggerObjectCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag(TRIGGER_MODULE_NAME, processName=cms.InputTag.skipCurrentProcess()),
        karmaRunSrc = cms.InputTag("karmaEvents"),
        triggerResultsSrc = cms.InputTag("TriggerResults", "", "HLT"),
    )
)
