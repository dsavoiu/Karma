from DijetAnalysis.Core.dijetPrelude_cff import *


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles="file://{}".format(os.path.realpath("../../../../Skimming/test/FullSkim/testFullSkim_out.root"))
    options.isData=1
    options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
    #options.edmOut="testSkim_out.root"
    options.maxEvents=1000
    options.dumpPython=1
    options.weightForStitching = 1.0
else:
    # -- running on grid node
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    #options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
    options.dumpPython=False
    options.reportEvery = 100000 #int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]
    options.weightForStitching = 1.0


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from DijetAnalysis.Analysis.JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer
from DijetAnalysis.Analysis.CorrectedValidJetsProducer_cfi import dijetCorrectedValidJetsProducer
from DijetAnalysis.Analysis.CorrectedMETsProducer_cfi import dijetCorrectedMETsProducer
from DijetAnalysis.Analysis.NtupleProducer_cfi import dijetNtupleProducer


# -- configure output ROOT file used by TFileService
process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("output.root"),
    closeFileFast = cms.untracked.bool(True),
)


class DijetAnalysis:
    def __init__(self, process):
        self._process = process
        self._pipeline_sequences = {}

    def _init_modules(self, jet_algo_name):
        setattr(
            self._process,
            "correctedJets{}".format(jet_algo_name),
            dijetCorrectedValidJetsProducer.clone(
                # -- input sources
                dijetEventSrc = cms.InputTag("dijetEvents"),
                dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJets{}".format(jet_algo_name)),

                # -- other configuration
                jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017{RUN}_V11_DATA/Summer16_07Aug2017{RUN}_V11_DATA".format(
                    os.getenv('CMSSW_BASE'),
                    RUN="GH",
                ),
                jecAlgoName = cms.string(jet_algo_name),
                jecLevels = cms.vstring(
                    "L1FastJet",
                    "L2Relative",
                    "L2L3Residual",
                ),
                jecUncertaintyShift = cms.double(0.0),

                jetIDSpec = cms.string("2016"),   # use "None" for no object-based JetID
                jetIDWorkingPoint = cms.string("TightLepVeto"),
            )
        )

        setattr(
            self._process,
            "correctedMETs{}".format(jet_algo_name),
            dijetCorrectedMETsProducer.clone(
                # -- input sources
                dijetEventSrc = cms.InputTag("dijetEvents"),
                dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),
                dijetCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
            )
        )

        setattr(
            self._process,
            "jetTriggerObjectMap{}".format(jet_algo_name),
            dijetJetTriggerObjectMatchingProducer.clone(
                dijetEventSrc = cms.InputTag("dijetEvents"),
                dijetJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
                dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),
            )
        )

        # -- JEC-shifted collections

        for _suffix, _factor in zip(["JECUp", "JECDn"], [1.0, -1.0]):
            setattr(
                self._process,
                "correctedJets{}{}".format(jet_algo_name, _suffix),
                getattr(self._process, "correctedJets{}".format(jet_algo_name)).clone(
                    jecUncertaintyShift = cms.double(_factor),
                )
            )

            setattr(
                self._process,
                "correctedMETs{}{}".format(jet_algo_name, _suffix),
                dijetCorrectedMETsProducer.clone(
                    # -- input sources
                    dijetEventSrc = cms.InputTag("dijetEvents"),
                    dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),
                    dijetCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
                )
            )

            setattr(
                self._process,
                "jetTriggerObjectMap{}{}".format(jet_algo_name, _suffix),
                dijetJetTriggerObjectMatchingProducer.clone(
                    dijetEventSrc = cms.InputTag("dijetEvents"),
                    dijetJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
                    dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),
                )
            )


    def setup_pipeline(self, pipeline_name, jet_algo_name, jet_collection_suffix=""):

        assert pipeline_name not in self._pipeline_sequences

        # make sure pipeline with this name has not yet been initialized
        assert not hasattr(self._process, "ntuple{}".format(pipeline_name))

        setattr(self._process, "ntuple{}".format(pipeline_name),
            dijetNtupleProducer.clone(
                dijetJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)),
                #dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),  # no JEC

                dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)),

                dijetMETCollectionSrc = cms.InputTag("correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)),
                #dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),  # no Type-I correction

                isData = cms.bool(options.isData),

                #triggerEfficienciesFile = cms.string(
                #    #"{}/src/DijetAnalysis/Analysis/data/trigger_efficiencies/2016/trigger_efficiencies_bootstrapping_2018-09-24.root".format(os.getenv("CMSSW_BASE"))
                #    "{}/src/DijetAnalysis/Analysis/data/trigger_efficiencies/2016/trigger_efficiencies_bootstrapping_2019-01-12.root".format(os.getenv("CMSSW_BASE"))
                #),
            )
        )

        # filter ensuring the existence of a leading jet pair
        setattr(self._process, "jetPairFilter{}".format(pipeline_name),
            cms.EDFilter(
                "JetPairFilter",
                cms.PSet(
                    dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                )
            )
        )

        # filter ensuring that the leading jet is within eta
        setattr(self._process, "leadingJetRapidityFilter{}".format(pipeline_name),
            cms.EDFilter(
                "LeadingJetRapidityFilter",
                cms.PSet(
                    dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                    maxJetAbsRapidity = cms.double(3.0),
                )
            )
        )

        # filter ensuring that the leading jet is above pt threshold
        setattr(self._process, "leadingJetPtFilter{}".format(pipeline_name),
            cms.EDFilter(
                "LeadingJetPtFilter",
                cms.PSet(
                    dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                    minJetPt = cms.double(60),
                )
            )
        )

        # analyzer for writing out flat ntuple
        setattr(self._process, "pipeline{}".format(pipeline_name),
            cms.EDAnalyzer(
                "NtupleFlatOutput",
                cms.PSet(
                    isData = cms.bool(options.isData),
                    dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                    dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}".format(pipeline_name)),
                    #outputFileName = cms.string("output_flat.root"),  # deprecated: using TFileService instead
                    treeName = cms.string("Events"),
                    checkForCompleteness = cms.bool(False),
                )
            )
        )

        self._pipeline_sequences[pipeline_name] = cms.Sequence(
            getattr(self._process, "correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)) *
            getattr(self._process, "jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)) *
            getattr(self._process, "correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)) *
            getattr(self._process, "ntuple{}".format(pipeline_name)) *
            getattr(self._process, "jetPairFilter{}".format(pipeline_name)) *
            #getattr(self._process, "leadingJetRapidityFilter{}".format(pipeline_name)) *
            getattr(self._process, "leadingJetPtFilter{}".format(pipeline_name)) *
            getattr(self._process, "pipeline{}".format(pipeline_name))
        )

    # -- public API

    def configure(self):

        # -- init modules
        for _jet_radius in (4, 8):
            _jet_algo_name = "AK{}PFchs".format(_jet_radius)

            self._init_modules(_jet_algo_name)

        # -- configure pipelines

        self.setup_pipeline(pipeline_name="AK4PFCHSNominal", jet_algo_name='AK4PFchs')
        self.setup_pipeline(pipeline_name="AK4PFCHSJECUp", jet_algo_name='AK4PFchs', jet_collection_suffix='JECUp')
        self.setup_pipeline(pipeline_name="AK4PFCHSJECDn", jet_algo_name='AK4PFchs', jet_collection_suffix='JECDn')
        self.setup_pipeline(pipeline_name="AK8PFCHSNominal", jet_algo_name='AK8PFchs')
        self.setup_pipeline(pipeline_name="AK8PFCHSJECUp", jet_algo_name='AK8PFchs', jet_collection_suffix='JECUp')
        self.setup_pipeline(pipeline_name="AK8PFCHSJECDn", jet_algo_name='AK8PFchs', jet_collection_suffix='JECDn')

        # -- create paths for pipelines
        for _pipeline_name, _pipeline_sequence in sorted(self._pipeline_sequences.items()):
            setattr(
                self._process,
                "path{}".format(_pipeline_name),
                cms.Path(_pipeline_sequence)
            )

ana = DijetAnalysis(process)

ana.configure()


# -- must be called at the end
finalizeAndRun(process, outputCommands=['drop *'])


## selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
