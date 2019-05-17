import FWCore.PythonUtilities.LumiList as LumiList

from Karma.Common.Tools import KarmaOptions, KarmaProcess
from Karma.Common.Sequences.jetToolbox_cff import addJetToolboxSequences
from Karma.Common.Sequences.jetEnergyCorrections_cff import undoJetEnergyCorrections


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles="file://{}".format(os.path.realpath("/ceph/storage/c/dsavoiu/miniaod-test/data/test_JetHT2016G.root"))
    options.isData=1
    options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
    options.edmOut="testSkim_out.root"
    options.maxEvents=1000
    options.dumpPython=1
else:
    # -- running on grid node
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
    options.dumpPython=False
    options.reportEvery = int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)

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
from Karma.Skimming.VertexCollectionProducer_cfi import karmaVertexCollectionProducer

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

process.karmaTriggerObjects = karmaTriggerObjectCollectionProducer.clone(
    karmaRunSrc = cms.InputTag("karmaEvents"),
)
_accumulated_output_commands.append("keep *_karmaTriggerObjects_*_KARMA")

process.karmaVertices = karmaVertexCollectionProducer.clone()
_accumulated_output_commands.append("keep *_karmaVertices_*_KARMA")

mainSequence = cms.Sequence(
    process.karmaEvents *
    process.karmaEventHLTFilter *
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
process.karmaPFMETs = karmaPFMETCollectionProducer.clone()
mainSequence *= process.karmaPFMETs
_accumulated_output_commands.append("keep *_karmaPFMETs_*_KARMA")

process.karmaCHSMETs = karmaCHSMETCollectionProducer(process, isData=options.isData).clone()
mainSequence *= process.karmaCHSMETs
_accumulated_output_commands.append("keep *_karmaCHSMETs_*_KARMA")

process.path = cms.Path(mainSequence)

#_accumulated_output_commands.append("keep *_selectedPatTrigger_*_*")

# -- must be called at the end
finalizeAndRun(process, outputCommands=_accumulated_output_commands)

# selective writeout based on path decisions
process.edmOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('path')
)
