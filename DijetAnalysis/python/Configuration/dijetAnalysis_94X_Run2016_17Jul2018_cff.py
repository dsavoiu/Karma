"""
Karma dijet analysis config for skims of 94X miniAOD files
==========================================================

This analysis config should be used for 2016 Karma skims produced with
CMSSW 94X (e.g. from 17Jul2018 Re-MiniAOD or the corresponding Monte-Carlo).

To use:

    # import the module
    from Karma.DijetAnalysis.Configuration import dijetAnalysis_94X_Run2016_17Jul2018_cff

    # register the options
    options = dijetAnalysis_94X_Run2016_17Jul2018_cff.register_options(options)

    # configure the process
    dijetAnalysis_94X_Run2016_17Jul2018_cff.configure(process)


"""
import os
import FWCore.ParameterSet.Config as cms


def register_options(options):
    """Command-Line option flags used by the configuration below."""
    return (
        options
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
    )

def init_modules(process, options, jet_algo_name):
    '''Configure analysis modules and return module sequence'''

    # == JEC-corrected valid jets =========================================

    from Karma.DijetAnalysis.CorrectedValidJetsProducer_cfi import dijetCorrectedValidJetsProducer

    process.add_module(
        "correctedJets{}".format(jet_algo_name),
        dijetCorrectedValidJetsProducer.clone(
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
                "L2L3Residual",  # safe to apply in MC (files contain dummy value 1.0)
            ),
            jecUncertaintyShift = cms.double(0.0),

            #jetIDSpec = cms.string("2016"),   # use "None" for no object-based JetID
            #jetIDWorkingPoint = cms.string("TightLepVeto"),
            jetIDSpec = cms.string("None"),   # use "None" for no object-based JetID
        )
    )

    # == Corrected valid METs =============================================

    from Karma.DijetAnalysis.CorrectedMETsProducer_cfi import dijetCorrectedMETsProducer

    process.add_module(
        "correctedMETs{}".format(jet_algo_name),
        dijetCorrectedMETsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaMETCollectionSrc = cms.InputTag("karmaMETs"),

            # jets for type-I correction
            karmaCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),

            # -- other configuration
            typeICorrectionMinJetPt = cms.double(15),
            typeICorrectionMaxTotalEMFraction = cms.double(0.9),
        )
    )

    # == Jet--Trigger Object association map ==============================

    from Karma.DijetAnalysis.JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer

    process.add_module(
        "jetTriggerObjectMap{}".format(jet_algo_name),
        dijetJetTriggerObjectMatchingProducer.clone(
            primaryCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
            secondaryCollectionSrc = cms.InputTag("karmaTriggerObjects"),
        )
    )

    # == Jet--GenJet association map (MC only) ============================

    if not options.isData:

        from Karma.DijetAnalysis.JetGenJetMatchingProducer_cfi import dijetJetGenJetMatchingProducer

        process.add_module(
            "jetGenJetMap{}".format(jet_algo_name),
            dijetJetGenJetMatchingProducer.clone(
                primaryCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
                secondaryCollectionSrc = cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),
            )
        )


    # == JEC-shifted collections ==========================================

    for _suffix, _factor in zip(["JECUp", "JECDn"], [1.0, -1.0]):
        process.add_module(
            "correctedJets{}{}".format(jet_algo_name, _suffix),
            getattr(process, "correctedJets{}".format(jet_algo_name)).clone(
                jecUncertaintyShift = cms.double(_factor),
            )
        )

        process.add_module(
            "correctedMETs{}{}".format(jet_algo_name, _suffix),
            getattr(process, "correctedMETs{}".format(jet_algo_name)).clone(
                # jets for type-I correction
                karmaCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
            )
        )

        process.add_module(
            "jetTriggerObjectMap{}{}".format(jet_algo_name, _suffix),
            getattr(process, "jetTriggerObjectMap{}".format(jet_algo_name)).clone(
                karmaJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
            )
        )

        if not options.isData:
            process.add_module(
                "jetGenJetMap{}{}".format(jet_algo_name, _suffix),
                getattr(process, "jetGenJetMap{}".format(jet_algo_name)).clone(
                    karmaJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
                )
            )


def setup_pipeline(process, options, pipeline_name, jet_algo_name, jet_collection_suffix=""):
    from Karma.DijetAnalysis.NtupleProducer_cfi import dijetNtupleProducer

    process.add_module(
        "ntuple{}".format(pipeline_name),
        dijetNtupleProducer.clone(
            karmaJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)),
            karmaGenJetCollectionSrc = cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),

            karmaJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)),
            karmaJetGenJetMapSrc = cms.InputTag("jetGenJetMap{}{}".format(jet_algo_name, jet_collection_suffix)),

            karmaMETCollectionSrc = cms.InputTag("correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)),

            isData = cms.bool(options.isData),
            weightForStitching = cms.double(options.weightForStitching),
            npuMeanFile = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_data.txt".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),

            # YAML files specifying analysis binning
            flexGridFileDijetPtAve = cms.string(
                "{}/src/Karma/DijetAnalysis/data/binning/flexgrid_ys_yb_ptave.yml".format(os.getenv('CMSSW_BASE'))),
            flexGridFileDijetMass = cms.string(
                "{}/src/Karma/DijetAnalysis/data/binning/flexgrid_ys_yb_mass.yml".format(os.getenv('CMSSW_BASE'))),

            pileupWeightFile = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_ratio.root".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),
            pileupWeightHistogramName = "pileup",
        )
    )

    # filter ensuring the existence of a leading jet pair
    process.add_module(
        "jetPairFilter{}".format(pipeline_name),
        cms.EDFilter(
            "JetPairFilter",
            cms.PSet(
                dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
            )
        )
    )

    # note: choose to apply these filters in PostProcessing

    ## # filter ensuring that the leading jet is within eta
    ## process.add_module(
    ##     "leadingJetRapidityFilter{}".format(pipeline_name),
    ##     cms.EDFilter(
    ##         "LeadingJetRapidityFilter",
    ##         cms.PSet(
    ##             dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
    ##             maxJetAbsRapidity = cms.double(3.0),
    ##         )
    ##     )
    ## )
    ##
    ## # filter ensuring that the leading jet is above pt threshold
    ## process.add_module(
    ##     "leadingJetPtFilter{}".format(pipeline_name),
    ##     cms.EDFilter(
    ##         "LeadingJetPtFilter",
    ##         cms.PSet(
    ##             dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
    ##             minJetPt = cms.double(60),
    ##         )
    ##     )
    ## )

    # analyzer for writing out flat ntuple
    process.add_module(
        "pipeline{}".format(pipeline_name),
        cms.EDAnalyzer(
            "NtupleFlatOutput",
            cms.PSet(
                isData = cms.bool(options.isData),
                dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                karmaJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}".format(pipeline_name)),
                treeName = cms.string("Events"),
                checkForCompleteness = cms.bool(options.checkForCompleteness),
            )
        )
    )

    _pre_ntuple_sequence = cms.Sequence(
        getattr(process, "correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)) *
        getattr(process, "jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)) *
        getattr(process, "correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)))

    _post_ntuple_sequence = cms.Sequence(
        getattr(process, "ntuple{}".format(pipeline_name)) *
        getattr(process, "jetPairFilter{}".format(pipeline_name)) *
        #getattr(process, "leadingJetRapidityFilter{}".format(pipeline_name)) *
        #getattr(process, "leadingJetPtFilter{}".format(pipeline_name)) *
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
    for _jet_radius in (4, 8):
        _jet_algo_name = "AK{}PFCHS".format(_jet_radius)

        init_modules(process, options, jet_algo_name=_jet_algo_name)

    # -- configure pipelines

    setup_pipeline(process, options, pipeline_name="AK4PFCHSNominal", jet_algo_name='AK4PFCHS')
    setup_pipeline(process, options, pipeline_name="AK4PFCHSJECUp",   jet_algo_name='AK4PFCHS', jet_collection_suffix='JECUp')
    setup_pipeline(process, options, pipeline_name="AK4PFCHSJECDn",   jet_algo_name='AK4PFCHS', jet_collection_suffix='JECDn')
    setup_pipeline(process, options, pipeline_name="AK8PFCHSNominal", jet_algo_name='AK8PFCHS')
    setup_pipeline(process, options, pipeline_name="AK8PFCHSJECUp",   jet_algo_name='AK8PFCHS', jet_collection_suffix='JECUp')
    setup_pipeline(process, options, pipeline_name="AK8PFCHSJECDn",   jet_algo_name='AK8PFCHS', jet_collection_suffix='JECDn')

    # just in case we need it
    return process
