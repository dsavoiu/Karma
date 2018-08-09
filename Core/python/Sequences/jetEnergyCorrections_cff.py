#
# jetEnergyCorrections
# --------------------
#
#   Including this configuration fragment will some tools for
#   updating/removing JEC from pat::Jets
#

import FWCore.ParameterSet.Config as cms

from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection


def undoJetEnergyCorrections(process,
                             jet_algorithm_specs=('ak4', 'ak8'),
                             pu_subtraction_methods=('CHS')):

    _updated_product_label = 'NoJEC'

    _output_collection_names = []
    for _jet_algo_radius in jet_algorithm_specs:
        for _pu_method in pu_subtraction_methods:
            _jet_collection_label = "{}PF{}".format(_jet_algo_radius.upper(), _pu_method.lower())
            _postfix = ""
            if _jet_algo_radius.upper() == "AK8":
                _postfix += "AK8"
            if _pu_method == "":
                _postfix += "PF"

            updateJetCollection(
                process,
                labelName = _updated_product_label,
                jetSource = cms.InputTag('slimmedJets'),
                jetCorrections = (
                    _jet_collection_label,
                    cms.vstring([]),  # no corrections
                    'None'
                )
            )
            _output_collection_names.append("updatedPatJets{}{}".format(_updated_product_label, _postfix))

            # remove any userfloats
            getattr(process, _output_collection_names[-1]).userData.userFloats.src = []
    
    return _output_collection_names
