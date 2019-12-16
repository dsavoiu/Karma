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

JET_TAG_LIST_FOR_DATA = [
    "pfTrackCountingHighEffBJetTags",
    "pfSecondaryVertexTagInfos",
    "pfCombinedSecondaryVertexV2BJetTags",
    "softPFElectronsTagInfos",
    "softPFMuonsTagInfos",
    "pfInclusiveSecondaryVertexFinderTagInfos",
    "pfCombinedMVAV2BJetTags",
    "pfCombinedInclusiveSecondaryVertexV2BJetTags",
    "pfSimpleSecondaryVertexHighPurBJetTags",
    "pfSimpleSecondaryVertexHighEffBJetTags",
    "pfJetBProbabilityBJetTags",
    "pfJetProbabilityBJetTags",
    "pfTrackCountingHighPurBJetTags",
]

def addJetToolboxSequences(process, isData,
                           jet_algorithm_specs=('ak4', 'ak8'),
                           pu_subtraction_methods=('', 'CHS'),
                           min_jet_pt=None,
                           do_pu_jet_id=False):

    # jet collections obtained with 'JetToolbox' CMSSW module:
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
    from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox

    _jet_collection_names = []

    # go through all combinations of jet radius and PU subtraction algorithms
    for _jet_algo_radius in jet_algorithm_specs:
        for _PU_method in pu_subtraction_methods:
            # -- first, make reco::PFJets using the jet toolbox
            jetToolbox(process,
                       _jet_algo_radius,
                       "jetToolbox{}{}".format(_jet_algo_radius, _PU_method),
                       'out',
                       dataTier='miniAOD',
                       runOnMC=not isData,
                       PUMethod=_PU_method,    # PU subtraction method
                       #bTagDiscriminators=[],  # do not skim btag discriminators
                       addPruning=False,
                       addSoftDrop=False,
                       addPrunedSubjets=False,
                       addNsub=False,
                       maxTau=6,
                       addTrimming=False,
                       addFiltering=False,
                       addNsubSubjets=False,
                       addPUJetID=do_pu_jet_id,
                       verbosity=2)

            # -- next, configure pT threshold for reco::PFJets
            if min_jet_pt is not None:
                _reco_pfjet_module = getattr(process, "{}PFJets{}".format(_jet_algo_radius, _PU_method))
                _reco_pfjet_module.jetPtMin = min_jet_pt  # doesn't seem to work

            # # add PUJetID calculator and evaluator to process
            # if _do_PUJetID:
            #     process.path *= getattr(process, "{}PF{}pileupJetIdCalculator".format(_jet_algo_radius.upper(), _PU_method))
            #     process.path *= getattr(process, "{}PF{}pileupJetIdEvaluator".format(_jet_algo_radius.upper(), _PU_method))

            # -- then, make pat::Jets
            patJetCollectionName = "{}PF{}".format(_jet_algo_radius.upper(), _PU_method)
            assert not hasattr(process, patJetCollectionName)

            _seq_data = cms.Sequence()
            for _tag in JET_TAG_LIST_FOR_DATA:
                try:
                    _seq_data *= getattr(process, "{}{}".format(_tag, patJetCollectionName))
                except AttributeError as _err:
                    print("[karmaJetToolbox] WARNING: Not adding jet tag '{}' to '{}' jets due to error: {}".format(_tag, patJetCollectionName, _err))

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
            if min_jet_pt is not None:
                _pat_jet_module = getattr(process, "selectedPatJets{}".format(patJetCollectionName))
                _pat_jet_module.cut = "pt()>{:f}".format(min_jet_pt)

            print "[karmaJetToolbox] Add pat::Jet collection '{}'".format(patJetCollectionName)
            _jet_collection_names.append("selectedPatJets{}".format(patJetCollectionName))

    # cleanup unused modules added by jet toolbox
    del process.out  # jettoolbox test rootfile

    # associate all tasks on the endpath with the path and remove the endpath
    for _task in process.endpath._tasks:
        process.paths['path'].associate(_task)
    del process.endpath

    return _jet_collection_names
