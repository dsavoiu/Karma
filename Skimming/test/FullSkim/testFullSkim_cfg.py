import FWCore.PythonUtilities.LumiList as LumiList

from DijetAnalysis.Core.dijetPrelude_cff import *
#from DijetAnalysis.Core.Sequences.jetToolbox_cff import addJetToolboxSequences
from DijetAnalysis.Core.Sequences.jetEnergyCorrections_cff import undoJetEnergyCorrections


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../data/test_JetHT2016G.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
options.edmOut="testFullSkim_out.root"
options.maxEvents=-1 #10000
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)

# modules will add to this list to register a product
# for writeout
_accumulated_output_commands = ['drop *']


# -- only process certified runs and lumisections
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

# don't use JetToolbox to recluster jets
# addJetToolboxSequences(process,
#                        isData=options.isData,
#                        jet_algorithm_specs=('ak4',),
#                        pu_subtraction_methods=('', 'CHS'),
#                        do_pu_jet_id=False)

from DijetAnalysis.Skimming.TriggerObjectCollectionProducer_cfi import dijetTriggerObjectCollectionProducer
from DijetAnalysis.Skimming.JetCollectionProducer_cfi import dijetJetCollectionProducer
from DijetAnalysis.Skimming.EventProducer_cfi import dijetEventProducer

from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
    src = cms.InputTag("offlineSlimmedPrimaryVertices"),
    filterParams = pvSelector.clone(
        maxZ = 24.0
    ),  # ndof >= 4, rho <= 2
)

process.dijetEvents = dijetEventProducer.clone(
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


preSequence = cms.Sequence(
    process.dijetEvents *
    process.dijetEventHLTFilter *
    process.dijetTriggerObjects
);


# uncorrect pat::Jets for JEC
uncorrected_jet_collection_names = undoJetEnergyCorrections(
    process,
    jet_algorithm_specs=('ak4',),
    pu_subtraction_methods=('CHS',)
)

# create "dijet::Jet" collections for JEC-uncorrected pat::Jets
for _jet_collection_name in uncorrected_jet_collection_names:
    _module_name = "dijet{}{}".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
    setattr(
        process,
        _module_name,
        dijetJetCollectionProducer.clone(
            inputCollection = cms.InputTag(_jet_collection_name),
        )
    )
    _accumulated_output_commands.extend([
        "keep *_{}_*_DIJET".format(_module_name),
    ])
    preSequence *= getattr(process, _jet_collection_name)


process.path = cms.Path(preSequence)


_accumulated_output_commands.append("keep *_selectedPatTrigger_*_*")

# -- must be called at the end
finalizeAndRun(process, outputCommands=_accumulated_output_commands)

# selective writeout based on path decisions
process.edmOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('path')
)
