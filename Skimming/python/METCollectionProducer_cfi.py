import FWCore.ParameterSet.Config as cms


dijetPFMETCollectionProducer = cms.EDProducer(
    "METCollectionProducer",
    cms.PSet(
        # take default PAT::MET from RECO (==PFMet)
        inputCollection = cms.InputTag("slimmedMETs", "", "RECO"),
    )
)

def dijetCHSMETCollectionProducer(process, isData):
    """create the producer for CHS MET, adding necessary prerequisites to the process"""

    # check that modules that will be registered do not already exist in process"
    for _attr in ('packedPFCandidatesCHSNotFromPV', 'packedPFCandidatesCHS'):
        if hasattr(process, _attr):
            raise ValueError("")

    # ------------------------------------------------------------------
    # official Prescription for calculating corrections and uncertainties on Missing Transverse Energy (MET):
    # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription#Instructions_for_8_0_X_X_26_patc

    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

    # create collection of PF candidates likely coming from the primary vertex
    process.packedPFCandidatesCHSNotFromPV = cms.EDFilter('CandPtrSelector',
        src = cms.InputTag('packedPFCandidates'),
        cut = cms.string('fromPV==0')  # only loose selection (0)
    )

    process.packedPFCandidatesCHS = cms.EDFilter('CandPtrSelector',
        src = cms.InputTag('packedPFCandidates'),
        cut = cms.string('fromPV() > 0')
    )

    # -- recompute the pat::MET from CHS candidates to obtain CHS met

    # the following lines are for default MET for Type1 corrections
    # If you only want to re-correct for JEC and get the proper uncertainties for the default MET
    runMetCorAndUncFromMiniAOD(
        process,
        isData=isData,
        pfCandColl='packedPFCandidatesCHS',
        recoMetFromPFCs=True
    )

    # ------------------------------------------------------------------

    return cms.EDProducer(
        "METCollectionProducer",
        cms.PSet(
            # take recomputed PAT::MET from the current process (==CHSMet)
            inputCollection = cms.InputTag("slimmedMETs"),
        )
    )

    ## register the sequence in process
    #_sequence = cms.Sequence(
    #    process.packedPFCandidatesCHSNotFromPV,
    #    process.packedPFCandidatesCHS,
    #    process.dijetCHSMETProducer
    #)
    #setattr(process, sequence_name, _sequence)
    #
    #return _sequence
