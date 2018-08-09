#
# jetToolbox
# ----------
#
#   Including this configuration fragment will re-cluster jets
#   down to a specified pT threshold using the 'JetToolbox' CMSSW
#   package.
#
#       rouch

import FWCore.ParameterSet.Config as cms

def addJetToolboxSequences(process, isData,
                           jet_algorithm_specs=('ak4',),
                           pu_subtraction_methods=('', 'CHS'),
                           do_pu_jet_id=False):

    # jet collections obtained with 'JetToolbox' CMSSW module:
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
    from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox

    # go through all combinations of jet radius and PU subtraction algorithms
    for _jet_algo_radius in jet_algorithm_specs:
        for _PU_method in pu_subtraction_methods:
            # -- first, make reco::PFJets using the jet toolbox
            _seq_name = "jetToolbox{}{}".format(_jet_algo_radius, _PU_method)
            jetToolbox(process,
                       _jet_algo_radius,
                       _seq_name,
                       'out',
                       miniAOD=True,
                       runOnMC=not isData,
                       JETCorrPayload="None",  # do *not* correct jets with JEC
                       PUMethod=_PU_method,    # PU subtraction method
                       addPruning=False,
                       addSoftDrop=False,
                       addPrunedSubjets=False,
                       addNsub=False,
                       maxTau=6,
                       addTrimming=False,
                       addFiltering=False,
                       addNsubSubjets=False,
                       addPUJetID=do_pu_jet_id)

            # # add PUJetID calculator and evaluator to process
            # if _do_PUJetID:
            #     process.path *= getattr(process, "{}PF{}pileupJetIdCalculator".format(_jet_algo_radius.upper(), _PU_method))
            #     process.path *= getattr(process, "{}PF{}pileupJetIdEvaluator".format(_jet_algo_radius.upper(), _PU_method))

            # -- then, make pat::Jets
            patJetCollectionName = "{}PF{}".format(_jet_algo_radius.upper(), _PU_method)
            assert not hasattr(process, patJetCollectionName)

            _seq_data = cms.Sequence(
                getattr(process, "pfImpactParameterTagInfos{}".format(patJetCollectionName))*
                getattr(process, "pfTrackCountingHighEffBJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfSecondaryVertexTagInfos{}".format(patJetCollectionName))*
                getattr(process, "pfCombinedSecondaryVertexV2BJetTags{}".format(patJetCollectionName))*
                getattr(process, "softPFElectronsTagInfos{}".format(patJetCollectionName))*
                getattr(process, "softPFMuonsTagInfos{}".format(patJetCollectionName))*
                getattr(process, "pfInclusiveSecondaryVertexFinderTagInfos{}".format(patJetCollectionName))*
                getattr(process, "pfCombinedMVAV2BJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfCombinedInclusiveSecondaryVertexV2BJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfSimpleSecondaryVertexHighPurBJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfSimpleSecondaryVertexHighEffBJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfJetBProbabilityBJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfJetProbabilityBJetTags{}".format(patJetCollectionName))*
                getattr(process, "pfTrackCountingHighPurBJetTags{}".format(patJetCollectionName))
            )
            
            if not isData:
                _seq_mc = cms.Sequence(
                    getattr(process, "patJetPartons")*
                    getattr(process, "patJetFlavourAssociation{}".format(patJetCollectionName))*
                    getattr(process, "patJetPartonMatch{}".format(patJetCollectionName))*
                    getattr(process, "patJetGenJetMatch{}".format(patJetCollectionName))
                )
                patSequence = cms.Sequence(
                    _seq_data * _seq_mc *
                    getattr(process, "patJets{}".format(patJetCollectionName))*
                    getattr(process, "selectedPatJets{}".format(patJetCollectionName))
                )
            else:
                patSequence = cms.Sequence(
                    _seq_data *
                    getattr(process, "patJets{}".format(patJetCollectionName))*
                    getattr(process, "selectedPatJets{}".format(patJetCollectionName))
                )
            setattr(process, patJetCollectionName, patSequence)
