import os

import FWCore.ParameterSet.Config as cms

import FWCore.PythonUtilities.LumiList as LumiList

from Karma.Common.Tools import KarmaOptions, KarmaProcess


# set up and parse command-line options
options = (
    KarmaOptions()
        .setDefault('inputFiles', "file:///storage/9/dsavoiu/test_miniAOD/test_DoubleEG_Run2016G_17Jul2018_MINIAOD_10events.root")
        .setDefault('isData', True)
        .setDefault('globalTag', "94X_dataRun2_v10")
        .setDefault('outputFile', "testEDMSkim_out.root")
        .setDefault('maxEvents', 100)
        .setDefault('dumpPython', True)
).parseArguments()


# create the process
process = KarmaProcess(
    "EDMSKIM",
    input_files=options.inputFiles,
    max_events=options.maxEvents,
    global_tag=options.globalTag,
    edm_out=options.outputFile,
    num_threads=1
)

# create the main module path
process.add_path('path')

# enable verbose log file output
#enableVerboseLogging(process)


# == configure CMSSW modules ==========================================

# -- Jets (default from miniAOD) --------------------------------------

# just write out miniAOD jets
process.add_output_commands(
    'keep patJets_slimmedJets_*_*',
    'keep patJets_slimmedJetsAK8_*_*',
)

# -- Jets (from miniAOD, but with possibly new JECs from GT) ----------

from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection

updateJetCollection(
    process,
    jetSource = cms.InputTag('slimmedJets'),
    labelName = 'UpdatedJEC',
    jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), 'None')  # Update: Safe to always add 'L2L3Residual' as MC contains dummy L2L3Residual corrections (always set to 1)
)

updateJetCollection(
    process,
    jetSource = cms.InputTag('slimmedJetsAK8'),
    labelName = 'UpdatedJECAK8',
    jetCorrections = ('AK8PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), 'None')  # Update: Safe to always add 'L2L3Residual' as MC contains dummy L2L3Residual corrections (always set to 1)
)

process.jecSequence = cms.Sequence(process.patJetCorrFactorsUpdatedJEC * process.updatedPatJetsUpdatedJEC)
process.jecSequenceAK8 = cms.Sequence(process.patJetCorrFactorsUpdatedJECAK8 * process.updatedPatJetsUpdatedJECAK8)

process.path *= process.jecSequence
process.path *= process.jecSequenceAK8

process.add_output_commands(
    'keep patJets_updatedPatJetsUpdatedJEC_*_*',
    'keep patJets_updatedPatJetsUpdatedJECAK8_*_*',
)

# -- Jets (reclustered with jet toolbox) ------------------------------

from Karma.Common.Sequences.jetToolbox_cff import addJetToolboxSequences

# create reclustering sequences

jet_collection_names = []

# AK4CHS jets (include pileupJetID)
jet_collection_names += addJetToolboxSequences(
    process, isData=options.isData,
    min_jet_pt=15,
    jet_algorithm_specs=('ak4',),
    pu_subtraction_methods=('CHS',),
    do_pu_jet_id=True
)

# AK8CHS jets (no pileupJetID available)
jet_collection_names += addJetToolboxSequences(
    process, isData=options.isData,
    min_jet_pt=15,
    jet_algorithm_specs=('ak8',),
    pu_subtraction_methods=('CHS',),
    do_pu_jet_id=False
)

# AK4Puppi and AK8Puppi jets
jet_collection_names += addJetToolboxSequences(
    process, isData=options.isData,
    min_jet_pt=15,
    jet_algorithm_specs=('ak4', 'ak8',),
    pu_subtraction_methods=('Puppi',),
    do_pu_jet_id=False
)

# put reclustering sequences on path
for _jet_collection_name in jet_collection_names:
    process.path *= getattr(process, _jet_collection_name)
    # write out reclustered jets
    process.add_output_commands('keep patJets_{}_*_*'.format(_jet_collection_name))

# -- Jet ID (precomputed and embedded as userInts) -------------------

for _jet_collection_name in jet_collection_names:
    _id_producer_name = "{}IDValueMap".format(_jet_collection_name)
    _enriched_jet_collection_name = "{}WithJetIDUserData".format(_jet_collection_name)

    # produce the jet id value map
    setattr(
        process,
        _id_producer_name,
        cms.EDProducer("PatJetIDValueMapProducer",
            filterParams = cms.PSet(
                version = cms.string('WINTER16'),
                quality = cms.string('TIGHTLEPVETO'),
            ),
            src = cms.InputTag(_jet_collection_name)
        )
    )

    # embed jet id information in pat::Jet itself
    setattr(
        process,
        _enriched_jet_collection_name,
        cms.EDProducer("PATJetUserDataEmbedder",
             src = cms.InputTag(_jet_collection_name),
             userInts = cms.PSet(
                tightIdLepVeto = cms.InputTag(_id_producer_name),
             ),
        )
    )

    # add modules to path
    process.path *= getattr(process, _id_producer_name)
    process.path *= getattr(process, _enriched_jet_collection_name)

    # wite out ID-enriched jet collection
    process.add_output_commands(
        'keep patJets_{}_*_*'.format(_enriched_jet_collection_name)
    )

# -- MET --------------------------------------------------------------

from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

# run this to keep MET Type-I correction up-to-date with currently applied JECs
runMetCorAndUncFromMiniAOD(
   process,
   isData=True,
)

process.path *= process.fullPatMetSequence

process.add_output_commands(
    'keep patMETs_slimmedMETs_*_*',
)

# -- Electrons --------------------------------------------------------

# just write out miniAOD electrons
process.add_output_commands(
    "keep patElectrons_slimmedElectrons_*_*",
)

# Note: electron scale/smearing correction information is contained in
# the following userFloats: 'ecalEnergyPreCorr' and 'ecalEnergyPostCorr'

# Note: electron ID information is stored in corresponding userFloats,
# e.g. 'cutBasedElectronID-Summer16-80X-V1-loose'


# -- Muons ------------------------------------------------------------

# just write out miniAOD muons
process.add_output_commands(
    "keep patMuons_slimmedMuons_*_*",
)

# == END configure CMSSW modules ======================================

# == configure Karma modules ==========================================



# == END configure Karma modules ======================================


# for debugging: dump entire cmsRun python configuration
if options.dumpPython:
    print "[karmaPrelude] Dumping Python configuration..."
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
