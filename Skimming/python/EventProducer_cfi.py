import FWCore.ParameterSet.Config as cms


def karmaEventProducer(isData):
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
            writeOutTriggerPrescales = cms.bool(False),

            # name of the HLT process (for HLTConfigProvider)
            hltProcessName = cms.string("HLT"),

            # HLTPrescaleProvider (similar to HLTConfigProvider) configuration
            hltConfigAndPrescaleProvider = cms.PSet(
                l1GtRecordInputTag = cms.InputTag("l1GtTriggerMenuLite"),
                l1GtReadoutRecordInputTag = cms.InputTag(""),
                l1GtTriggerMenuLiteInputTag =  cms.InputTag("l1GtTriggerMenuLite"),
            ),

            # interesting trigger paths must match one of these regexes:
            hltRegexes = cms.vstring("HLT_(AK8)?PFJet[0-9]+_v[0-9]+", "HLT_DiPFJetAve[0-9]+_v[0-9]+"),

            metFiltersSrc = cms.InputTag("TriggerResults", "", "RECO"),
            metFilterNames = cms.vstring(
                'Flag_METFilters',
                'Flag_HBHENoiseFilter',
                'Flag_HBHENoiseIsoFilter',
                'Flag_CSCTightHaloFilter',
                'Flag_CSCTightHaloTrkMuUnvetoFilter',
                'Flag_CSCTightHalo2015Filter',
                'Flag_globalTightHalo2016Filter',
                'Flag_globalSuperTightHalo2016Filter',
                'Flag_HcalStripHaloFilter',
                'Flag_hcalLaserEventFilter',
                'Flag_EcalDeadCellTriggerPrimitiveFilter',
                'Flag_EcalDeadCellBoundaryEnergyFilter',
                'Flag_goodVertices',
                'Flag_eeBadScFilter',
                'Flag_ecalLaserCorrFilter',
                'Flag_trkPOGFilters',
                'Flag_chargedHadronTrackResolutionFilter',
                'Flag_muonBadTrackFilter',
                'Flag_BadChargedCandidateFilter',
                'Flag_BadPFMuonFilter',
                'Flag_BadChargedCandidateSummer16Filter',
                'Flag_BadPFMuonSummer16Filter',
                'Flag_trkPOG_manystripclus53X',
                'Flag_trkPOG_toomanystripclus53X',
                'Flag_trkPOG_logErrorTooManyClusters',
            )
        )
    )
