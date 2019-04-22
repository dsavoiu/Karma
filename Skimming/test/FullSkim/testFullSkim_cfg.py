import FWCore.PythonUtilities.LumiList as LumiList

from DijetAnalysis.Core.dijetPrelude_cff import *
from DijetAnalysis.Core.Sequences.jetToolbox_cff import addJetToolboxSequences
from DijetAnalysis.Core.Sequences.jetEnergyCorrections_cff import undoJetEnergyCorrections


# -- override CLI options for test
#options.inputFiles="file://{}".format(os.path.realpath("../../data/test_JetHT2016G.root"))
options.inputFiles="file://{}".format("/ceph/storage/c/dsavoiu/miniaod-test/data/test_JetHT2016G.root")
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
options.edmOut="testFullSkim_out_1000.root"
#options.maxEvents=1000
options.edmOut="testFullSkim_out.root"
options.maxEvents=-1
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)

# modules will add to this list to register a product
# for writeout
_accumulated_output_commands = ['drop *']


# -- only process certified runs and lumisections
if options.isData:
    process.source.lumisToProcess = LumiList.LumiList(
        filename = os.path.realpath("{}/src/DijetAnalysis/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE")))
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

from DijetAnalysis.Skimming.TriggerObjectCollectionProducer_cfi import dijetTriggerObjectCollectionProducer
from DijetAnalysis.Skimming.JetCollectionProducer_cfi import dijetJets
from DijetAnalysis.Skimming.METCollectionProducer_cfi import dijetPFMETCollectionProducer, dijetCHSMETCollectionProducer
from DijetAnalysis.Skimming.EventProducer_cfi import dijetEventProducer
from DijetAnalysis.Skimming.VertexCollectionProducer_cfi import dijetVertexCollectionProducer

from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
    src = cms.InputTag("offlineSlimmedPrimaryVertices"),
    filterParams = pvSelector.clone(
        maxZ = 24.0
    ),  # ndof >= 4, rho <= 2
)

process.dijetEvents = dijetEventProducer(isData=options.isData).clone(
    goodPrimaryVerticesSrc = cms.InputTag("goodOfflinePrimaryVertices"),
)
_accumulated_output_commands.append("keep *_dijetEvents_*_DIJET")

# filter events for which "interesting" HLT paths fired
process.dijetEventHLTFilter = cms.EDFilter("EventHLTFilter",
    cms.PSet(
        dijetEventSrc = cms.InputTag("dijetEvents")
    )
)
_accumulated_output_commands.append("drop *_dijetEventHLTFilter_*_DIJET")

process.dijetTriggerObjects = dijetTriggerObjectCollectionProducer.clone(
    dijetRunSrc = cms.InputTag("dijetEvents"),
)
_accumulated_output_commands.append("keep *_dijetTriggerObjects_*_DIJET")

process.dijetVertices = dijetVertexCollectionProducer.clone()
_accumulated_output_commands.append("keep *_dijetVertices_*_DIJET")

mainSequence = cms.Sequence(
    process.dijetEvents *
    process.dijetEventHLTFilter *
    process.dijetTriggerObjects *
    process.dijetVertices
);


# use JetToolbox to recluster (JEC-uncorrected) jets
uncorrected_jet_collection_names = addJetToolboxSequences(
    process,
    isData=options.isData,
    jet_algorithm_specs=('ak4', 'ak8'),
    pu_subtraction_methods=('CHS',),
    do_pu_jet_id=False)

# create "dijet::Jet" collections for JEC-uncorrected pat::Jets
for _jet_collection_name in uncorrected_jet_collection_names:
    _module_name = "dijet{}{}".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
    setattr(
        process,
        _module_name,
        dijetJets.clone(
            inputCollection = cms.InputTag(_jet_collection_name),
        )
    )
    _accumulated_output_commands.extend([
        "keep *_{}_*_DIJET".format(_module_name),
    ])
    mainSequence *= getattr(process, _jet_collection_name)

# create "dijet::MET" collections for (uncorrected) PF and CHS Mets
process.dijetPFMETs = dijetPFMETCollectionProducer.clone()
mainSequence *= process.dijetPFMETs
_accumulated_output_commands.append("keep *_dijetPFMETs_*_DIJET")

process.dijetCHSMETs = dijetCHSMETCollectionProducer(process, isData=options.isData).clone()
mainSequence *= process.dijetCHSMETs
_accumulated_output_commands.append("keep *_dijetCHSMETs_*_DIJET")

process.path = cms.Path(mainSequence)

#_accumulated_output_commands.append("keep *_selectedPatTrigger_*_*")

# -- must be called at the end
finalizeAndRun(process, outputCommands=_accumulated_output_commands)

# selective writeout based on path decisions
process.edmOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('path')
)
