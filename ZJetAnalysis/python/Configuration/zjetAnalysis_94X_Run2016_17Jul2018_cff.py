"""
Karma Z+Jets analysis config for skims of 94X miniAOD files
===========================================================

This analysis config should be used for 2016 Karma skims produced with
CMSSW 94X (e.g. from 17Jul2018 Re-MiniAOD or the corresponding Monte-Carlo).

To use:

    # import the module
    from Karma.ZJetAnalysis.Configuration import zjetAnalysis_94X_Run2016_17Jul2018_cff

    # register the options
    options = zjetAnalysis_94X_Run2016_17Jul2018_cff.register_options(options)

    # configure the process
    zjetAnalysis_94X_Run2016_17Jul2018_cff.configure(process)


"""
import os
import FWCore.ParameterSet.Config as cms


JEC_LEVELS_SPEC = dict(
    Raw = cms.vstring(),
    L1 = cms.vstring("L1FastJet"),
    L1L2L3 = cms.vstring("L1FastJet", "L2Relative"),
    L1L2L3Res = cms.vstring("L1FastJet", "L2Relative", "L2L3Residual"),
)

def register_options(options):
    """Command-Line option flags used by the configuration below."""
    return (
        options
            .register('channel',
                      type_=str,
                      default=None,
                      description="Analysis channel. Either 'mm' or 'ee'")
            .register('jecVersion',
                      type_=str,
                      default=None,
                      description="Tag of JEC version to use for e.g. JEC uncertainties.")
            .register('checkForCompleteness',
                      type_=bool,
                      default=False,
                      description=("(for testing) If True, will run some checks on the "
                                   "Ntuple output to ensure all branches are written out "
                                   "and no branch is omitted."))
            .register('weightForStitching',
                      type_=float,
                      default=1.0,
                      description=("(deprecated) The output branch 'weightForStitching' "
                                   "will contain this value for each event. Can then be "
                                   "used when stitching together different samples."))
            .register('edmOut',
                      type_=bool,
                      default=False,
                      description="(for testing only) Write out EDM file.")
    )

def init_modules(process, options, jet_algo_name):
    '''Configure analysis modules and return module sequence'''

    # == JEC-corrected valid jets =========================================

    from Karma.Common.Producers.CorrectedValidJetsProducer_cfi import karmaCorrectedValidJetsProducer

    _jet_producer_template = karmaCorrectedValidJetsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaJetCollectionSrc = cms.InputTag("karmaSelectedPatJets{}".format(jet_algo_name)),

            # -- other configuration
            jecVersion = "{}/src/JECDatabase/textFiles/{jec_version}_{data_or_mc}/{jec_version}_{data_or_mc}".format(
                os.getenv('CMSSW_BASE'),
                jec_version=options.jecVersion,
                data_or_mc="DATA" if options.isData else "MC",
            ),
            jecAlgoName = cms.string(jet_algo_name.replace('CHS', 'chs')),
            jecLevels = cms.vstring(
                "L1FastJet",
                "L2Relative",
                "L2L3Residual",
            ),
            jecUncertaintyShift = cms.double(0.0),

            #jetIDSpec = cms.string("2016"),   # use "None" for no object-based JetID
            #jetIDWorkingPoint = cms.string("TightLepVeto"),
            jetIDSpec = cms.string("None"),   # use "None" for no object-based JetID
        )

    # == Corrected valid METs =============================================

    from Karma.Common.Producers.CorrectedMETsProducer_cfi import karmaCorrectedMETsProducer

    _met_producer_template = karmaCorrectedMETsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaMETCollectionSrc = cms.InputTag("karmaMETs"),

            # jets for type-I correction
            karmaCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),

            # -- other configuration
            typeICorrectionMinJetPt = cms.double(15),
            typeICorrectionMaxTotalEMFraction = cms.double(0.9),
        )

    # == Jet--Leptons association maps ====================================

    from Karma.Common.Producers.JetMatchingProducers_cfi import karmaJetMuonMatchingProducer, karmaJetElectronMatchingProducer

    process.add_module(
        "jetMuonMap{}".format(jet_algo_name),
        karmaJetMuonMatchingProducer.clone(
            primaryCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
            secondaryCollectionSrc = cms.InputTag("karmaMuons"),
        )
    )

    process.add_module(
        "jetElectronMap{}".format(jet_algo_name),
        karmaJetElectronMatchingProducer.clone(
            primaryCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
            secondaryCollectionSrc = cms.InputTag("karmalectrons"),
        )
    )

    # == Jet--GenJet association map (MC only) ============================

    from Karma.Common.Producers.JetMatchingProducers_cfi import karmaJetGenJetMatchingProducer

    _genjet_map_producer_template = karmaJetGenJetMatchingProducer.clone(
        primaryCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
        secondaryCollectionSrc = cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),
        maxDeltaR = cms.double(0.2),
    )

    # == jet collections with different JEC levels ================================

    for _suffix, _spec in JEC_LEVELS_SPEC.items():
        process.add_module(
            "correctedJets{}{}".format(jet_algo_name, _suffix),
            _jet_producer_template.clone(
                jecLevels = _spec,
            )
        )

        process.add_module(
            "correctedMETs{}{}".format(jet_algo_name, _suffix),
            _met_producer_template.clone(
                # jets for type-I correction
                karmaCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
            )
        )

        if not options.isData:
            process.add_module(
                "jetGenJetMap{}{}".format(jet_algo_name, _suffix),
                _genjet_map_producer_template.clone(
                    primaryCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
                )
            )


def setup_pipeline(process, options, pipeline_name, jet_algo_name, jet_collection_suffix=""):
    from Karma.ZJetAnalysis.NtupleProducer_cfi import zjetNtupleProducer

    process.add_module(
        "ntuple{}".format(pipeline_name),
        zjetNtupleProducer.clone(
            karmaJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)),
            karmaGenJetCollectionSrc = cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),

            karmaJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)),
            karmaJetGenJetMapSrc = cms.InputTag("jetGenJetMap{}{}".format(jet_algo_name, jet_collection_suffix)),

            karmaMETCollectionSrc = cms.InputTag("correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)),

            karmaElectronCollectionSrc = cms.InputTag("karmaElectrons"),
            karmaMuonCollectionSrc = cms.InputTag("karmaMuons"),

            isData = cms.bool(options.isData),
            channelSpec = cms.string(options.channel),
            weightForStitching = cms.double(options.weightForStitching),

            npuMeanFile = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_data.txt".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),

            pileupWeightFile = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_ratio.root".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),
            pileupWeightHistogramName = "pileup",
        )
    )

    # analyzer for writing out flat ntuple
    process.add_module(
        "pipeline{}".format(pipeline_name),
        cms.EDAnalyzer(
            "ZJetNtupleFlatOutput",
            cms.PSet(
                isData = cms.bool(options.isData),
                ntupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                karmaJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}".format(pipeline_name)),
                treeName = cms.string("Events"),
                checkForCompleteness = cms.bool(options.checkForCompleteness),
            )
        )
    )

    _pre_ntuple_sequence = cms.Sequence(
        getattr(process, "correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)) *
        getattr(process, "correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)))

    _post_ntuple_sequence = cms.Sequence(
        getattr(process, "ntuple{}".format(pipeline_name)) *
        getattr(process, "pipeline{}".format(pipeline_name))
    )

    _maybe_mc_specific_sequence = cms.Sequence()
    if not options.isData:
        _maybe_mc_specific_sequence *= getattr(process, "jetGenJetMap{}{}".format(jet_algo_name, jet_collection_suffix))

    _complete_pipeline_sequence = cms.Sequence(
        _pre_ntuple_sequence *
        _maybe_mc_specific_sequence *
        _post_ntuple_sequence
    )

    # create a cms.Path and put the pipeline on it
    process.add_path(
        "path{}".format(pipeline_name),
        cms.Path(_complete_pipeline_sequence)
    )


def configure(process, options):
    """Apply configuration to a process."""

    # create a TFileService for output
    process.TFileService = cms.Service(
        "TFileService",
        fileName = cms.string(options.outputFile),
        closeFileFast = cms.untracked.bool(True),
    )

    # -- init modules
    for _jet_radius in (4,):
        _jet_algo_name = "AK{}PFCHS".format(_jet_radius)

        init_modules(process, options, jet_algo_name=_jet_algo_name)

        # -- configure pipelines

        for _suffix, _spec in JEC_LEVELS_SPEC.items():
            setup_pipeline(process, options,
                pipeline_name="{}JEC{}".format(_jet_algo_name, _suffix),
                jet_algo_name=_jet_algo_name,
                jet_collection_suffix=_suffix)

    # just in case we need it
    return process
