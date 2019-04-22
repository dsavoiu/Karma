import FWCore.PythonUtilities.LumiList as LumiList

from Karma.Common.karmaPrelude_cff import *
from Karma.Common.Sequences.jetToolbox_cff import addJetToolboxSequences
from Karma.Common.Sequences.jetEnergyCorrections_cff import undoJetEnergyCorrections


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../data/test_QCDPt600to800_RunIISummer16MiniAODv2.root"))
#options.inputFiles="file://{}".format("/ceph/dsavoiu/miniaod-test/mc/test_QCDPt600to800_RunIISummer16MiniAODv2.root")
options.isData=0
options.globalTag="80X_mcRun2_asymptotic_2016_TrancheIV_v6"
#options.edmOut="testFullMCSkim_out_3000.root"
#options.maxEvents=3000
options.edmOut="testFullMCSkim_out.root"
options.maxEvents=-1
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("KARMA", num_threads=1)

# modules will add to this list to register a product
# for writeout
_accumulated_output_commands = ['drop *']


# -- only process certified runs and lumisections
if options.isData:
    process.source.lumisToProcess = LumiList.LumiList(
        filename = os.path.realpath("{}/src/Karma/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE")))
    ).getVLuminosityBlockRange()

## enable verbose log file output
#enableVerboseLogging(process)

# ignore errors from HLTPrescaleProvider (issued when
# no unique L1 prescale can be found for a HLT path)
process.MessageLogger.categories.append("HLTPrescaleProvider")
process.MessageLogger.cerr.HLTPrescaleProvider = cms.untracked.PSet(
    limit = cms.untracked.int32(2),
)

# -- configure CMSSW modules

from Karma.Skimming.TriggerObjectCollectionProducer_cfi import karmaTriggerObjectCollectionProducer
from Karma.Skimming.METCollectionProducer_cfi import karmaPFMETCollectionProducer, karmaCHSMETCollectionProducer
from Karma.Skimming.JetCollectionProducer_cfi import karmaJets
from Karma.Skimming.EventProducer_cfi import karmaEventProducer
from Karma.Skimming.GeneratorQCDInfoProducer_cfi import karmaGeneratorQCDInfoProducer
from Karma.Skimming.VertexCollectionProducer_cfi import karmaVertexCollectionProducer

from Karma.Skimming.GenJetCollectionProducer_cfi import karmaGenJetsAK4, karmaGenJetsAK8
from Karma.Skimming.GenParticleCollectionProducer_cfi import karmaGenParticleCollectionProducer

from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
    src = cms.InputTag("offlineSlimmedPrimaryVertices"),
    filterParams = pvSelector.clone(
        maxZ = 24.0
    ),  # ndof >= 4, rho <= 2
)

process.karmaEvents = karmaEventProducer(isData=options.isData).clone(
    goodPrimaryVerticesSrc = cms.InputTag("goodOfflinePrimaryVertices"),
)
_accumulated_output_commands.append("keep *_karmaEvents_*_KARMA")

# filter events for which "interesting" HLT paths fired
process.karmaEventHLTFilter = cms.EDFilter("EventHLTFilter",
    cms.PSet(
        karmaEventSrc = cms.InputTag("karmaEvents")
    )
)
_accumulated_output_commands.append("drop *_karmaEventHLTFilter_*_KARMA")

process.karmaGeneratorQCDInfos = karmaGeneratorQCDInfoProducer.clone(
    genEventInfoProductSrc = cms.InputTag("generator"),
)
_accumulated_output_commands.append("keep *_karmaGeneratorQCDInfos_*_KARMA")

process.karmaTriggerObjects = karmaTriggerObjectCollectionProducer.clone(
    karmaRunSrc = cms.InputTag("karmaEvents"),
)
_accumulated_output_commands.append("keep *_karmaTriggerObjects_*_KARMA")

process.karmaVertices = karmaVertexCollectionProducer.clone()
_accumulated_output_commands.append("keep *_karmaVertices_*_KARMA")

mainSequence = cms.Sequence(
    process.karmaEvents *
    process.karmaEventHLTFilter *
    process.karmaGeneratorQCDInfos *
    process.karmaTriggerObjects *
    process.karmaVertices
);


# use JetToolbox to recluster (JEC-uncorrected) jets
uncorrected_jet_collection_names = addJetToolboxSequences(
    process,
    isData=options.isData,
    jet_algorithm_specs=('ak4', 'ak8'),
    pu_subtraction_methods=('CHS',),
    do_pu_jet_id=False)

# create "karma::Jet" collections for JEC-uncorrected pat::Jets
for _jet_collection_name in uncorrected_jet_collection_names:
    _module_name = "karma{}{}".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
    setattr(
        process,
        _module_name,
        karmaJets.clone(
            inputCollection = cms.InputTag(_jet_collection_name),
        )
    )
    _accumulated_output_commands.extend([
        "keep *_{}_*_KARMA".format(_module_name),
    ])
    mainSequence *= getattr(process, _jet_collection_name)

# create "karma::MET" collections for (uncorrected) PF and CHS Mets
process.karmaPFMETs = karmaPFMETCollectionProducer.clone(
    # take default PAT::MET from PAT (==PFMet)
    inputCollection = cms.InputTag("slimmedMETs", "", "PAT"),
)
mainSequence *= process.karmaPFMETs
_accumulated_output_commands.append("keep *_karmaPFMETs_*_KARMA")

process.karmaCHSMETs = karmaCHSMETCollectionProducer(process, isData=options.isData).clone()
mainSequence *= process.karmaCHSMETs
_accumulated_output_commands.append("keep *_karmaCHSMETs_*_KARMA")

# -- MC-specific


# create GetParticle collection
process.karmaGenParticles = karmaGenParticleCollectionProducer.clone(
    inputCollection = cms.InputTag("prunedGenParticles"),
)
mainSequence *= process.karmaGenParticles
_accumulated_output_commands.append("keep *_karmaGenParticles_*_KARMA")

# create GetJet collections
process.karmaGenJetsAK4 = karmaGenJetsAK4.clone(
    inputCollection = cms.InputTag("ak4GenJetsNoNu"),
)
mainSequence *= process.karmaGenJetsAK4
_accumulated_output_commands.append("keep *_karmaGenJetsAK4_*_KARMA")

process.karmaGenJetsAK8 = karmaGenJetsAK4.clone(
    inputCollection = cms.InputTag("ak8GenJetsNoNu"),
)
mainSequence *= process.karmaGenJetsAK8
_accumulated_output_commands.append("keep *_karmaGenJetsAK8_*_KARMA")

process.path = cms.Path(mainSequence)

#_accumulated_output_commands.append("keep *_selectedPatTrigger_*_*")

# -- must be called at the end
finalizeAndRun(process, outputCommands=_accumulated_output_commands)

# selective writeout based on path decisions
process.edmOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('path')
)
