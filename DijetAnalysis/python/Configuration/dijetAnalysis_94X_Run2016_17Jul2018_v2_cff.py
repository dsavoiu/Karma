"""
Karma dijet analysis config for skims of 94X miniAOD files (v2)
==========================================================

This analysis config should be used for 2016 Karma skims produced with
CMSSW 94X (e.g. from 17Jul2018 Re-MiniAOD or the corresponding Monte-Carlo).

To use:

    # import the module
    from Karma.DijetAnalysis.Configuration import dijetAnalysis_94X_Run2016_17Jul2018_v2_cff

    # register the options
    options = dijetAnalysis_94X_Run2016_17Jul2018_v2_cff.register_options(options)

    # configure the process
    dijetAnalysis_94X_Run2016_17Jul2018_v2_cff.configure(process)


"""
import os
import FWCore.ParameterSet.Config as cms

JET_COLLECTIONS = ('AK4PFCHS', 'AK8PFCHS')
JEC_PIPELINES = {
    "JECNominal" : {'shift' :  0.0},
    #"JECUp" :      {'shift' :  1.0},
    #"JECDn" :      {'shift' : -1.0},
}
JER_PIPELINES = {
    "JERNominal" : {'variation' : 0},
    "JERUp" :      {'variation' : 1},
    "JERDn" :      {'variation' :-1},
}
JEC_UNCERTAINTY_SOURCE_SETS = {
    "AbsoluteStat":     {'sources': ["AbsoluteStat"]},
    "AbsoluteScale":    {'sources': ["AbsoluteScale"]},
    "AbsoluteMPFBias":  {'sources': ["AbsoluteMPFBias"]},
    "Fragmentation":    {'sources': ["Fragmentation"]},
    "SinglePionECAL":   {'sources': ["SinglePionECAL"]},
    "SinglePionHCAL":   {'sources': ["SinglePionHCAL"]},
    "FlavorQCD":        {'sources': ["FlavorQCD"]},
    "TimePtEta":        {'sources': ["TimePtEta"]},
    "RelativeJEREC1":   {'sources': ["RelativeJEREC1"]},
    "RelativeJEREC2":   {'sources': ["RelativeJEREC2"]},
    "RelativeJERHF":    {'sources': ["RelativeJERHF"]},
    "RelativePtBB":     {'sources': ["RelativePtBB"]},
    "RelativePtEC1":    {'sources': ["RelativePtEC1"]},
    "RelativePtEC2":    {'sources': ["RelativePtEC2"]},
    "RelativePtHF":     {'sources': ["RelativePtHF"]},
    "RelativeBal":      {'sources': ["RelativeBal"]},
    "RelativeSample":   {'sources': ["RelativeSample"]},
    "RelativeFSR":      {'sources': ["RelativeFSR"]},
    "RelativeStatFSR":  {'sources': ["RelativeStatFSR"]},
    "RelativeStatEC":   {'sources': ["RelativeStatEC"]},
    "RelativeStatHF":   {'sources': ["RelativeStatHF"]},
    "PileUpDataMC":     {'sources': ["PileUpDataMC"]},
    "PileUpPtRef":      {'sources': ["PileUpPtRef"]},
    "PileUpPtBB":       {'sources': ["PileUpPtBB"]},
    "PileUpPtEC1":      {'sources': ["PileUpPtEC1"]},
    "PileUpPtEC2":      {'sources': ["PileUpPtEC2"]},
    "PileUpPtHF":       {'sources': ["PileUpPtHF"]},
}
_ALL_JEC_UNCERTAINTY_SOURCES = set(_name for _spec in JEC_UNCERTAINTY_SOURCE_SETS.values() for _name in _spec['sources'])

# expand source sets to both 'Up' and 'Down' variations
for _unc_src_set, _unc_src_set_spec in JEC_UNCERTAINTY_SOURCE_SETS.items():
    del JEC_UNCERTAINTY_SOURCE_SETS[_unc_src_set]
    for _shift_dir, _shift_factor in zip(("Up", "Dn"), (1.0, -1.0)):
        JEC_UNCERTAINTY_SOURCE_SETS.update({_unc_src_set+_shift_dir: dict(_unc_src_set_spec, shift=_shift_factor)})


def register_options(options):
    """Command-Line option flags used by the configuration below."""
    return (
        options
            .register('jsonFilterFile',
                      type_=str,
                      default=None,
                      description="Path to JSON file containing certified runs and luminosity blocks.")
            .register('useHLTFilter',
                      type_=bool,
                      default=False,
                      description="If True, only events triggered by one of the skimmed paths will be "
                                  "written out.")
            .register('jetCollections',
                      type_=str,
                      default=[],
                      multiplicity='list',
                      description="The names of the jet collections to use (e.g. 'AK4PFCHS').")
            .register('jecVersion',
                      type_=str,
                      default=None,
                      description="Tag of JEC version to use for e.g. JEC uncertainties.")
            .register('jecFromGlobalTag',
                      type_=bool,
                      default=False,
                      description="If True, the JECs will be looked up in the conditions database "
                                   "(CondDB/Frontier) under the current global tag. If False, the "
                                   "text files for `jecVersion` will be used.")
            .register('jerVersion',
                      type_=str,
                      default=None,
                      description="Tag of JER version to use for e.g. jet smearing.")
            .register('jerMethod',
                      type_=str,
                      default='stochastic',
                      description="Method to use for JER smearing. One of: 'stochastic', 'hybrid'")
            .register('jetIDSpec',
                      type_=str,
                      default=None,
                      description="Version of Jet ID to use (e.g. '2016').")
            .register('jetIDWorkingPoint',
                      type_=str,
                      default=None,
                      description="Working point of Jet ID to use (e.g. 'TightLepVeto').")
            .register('prefiringWeightFilePath',
                      type_=str,
                      default="",
                      description="Path to ROOT file containing prefiring weights.")
            .register('prefiringWeightHistName',
                      type_=str,
                      default="",
                      description="Name of histogram inside prefiring weights file (e.g. 'L1prefiring_jetpt_2016BCD').")
            .register('useObjectBasedJetID',
                      type_=bool,
                      default=False,
                      description="If True, only jets passing the ID specified via 'jetIDSpec' and `jetIDWorkingPoint` will be considered valid.")
            .register('checkForCompleteness',
                      type_=bool,
                      default=False,
                      description=("(for testing) If True, will run some checks on the "
                                   "Ntuple output to ensure all branches are written out "
                                   "and no branch is omitted."))
            .register('stitchingWeight',
                      type_=float,
                      default=1.0,
                      description=("(deprecated) The output branch 'stitchingWeight' "
                                   "will contain this value for each event. Can then be "
                                   "used when stitching together different samples."))
            .register('doJECUncertaintySources',
                      type_=bool,
                      default=False,
                      description="Fill ntuple branch with JEC correction factors for individual JEC uncertainty sources.")
            .register('doPrescales',
                      type_=bool,
                      default=False,
                      description="Write out trigger prescales to Ntuple.")
            .register('edmOut',
                      type_=bool,
                      default=False,
                      description="(for testing only) Write out EDM file.")
    )


def _add_jet_maps(process, options, prefix, jet_algo_name):
    """convenience function for adding modules that produce AssociationMaps
    from a jet collection to other objects (trigger objects, gen-jets, leptons, etc.)"""

    # -- jet-to-trigger-object association map
    from Karma.Common.Producers.JetMatchingProducers_cfi import karmaJetTriggerObjectMatchingProducer
    process.add_module(
        "{}JetTriggerObjectMap{}".format(prefix, jet_algo_name),
        karmaJetTriggerObjectMatchingProducer.clone(
            primaryCollectionSrc = cms.InputTag("{}Jets{}".format(prefix, jet_algo_name)),
            secondaryCollectionSrc = cms.InputTag("karmaTriggerObjects"),
        )
    )

    # -- jet-to-lepton association maps
    from Karma.Common.Producers.JetMatchingProducers_cfi import karmaJetMuonMatchingProducer
    process.add_module(
        "{}JetMuonMap{}".format(prefix, jet_algo_name),
        karmaJetMuonMatchingProducer.clone(
            primaryCollectionSrc = cms.InputTag("{}Jets{}".format(prefix, jet_algo_name)),
            secondaryCollectionSrc = cms.InputTag("karmaMuons"),
        )
    )
    from Karma.Common.Producers.JetMatchingProducers_cfi import karmaJetElectronMatchingProducer
    process.add_module(
        "{}JetElectronMap{}".format(prefix, jet_algo_name),
        karmaJetElectronMatchingProducer.clone(
            primaryCollectionSrc = cms.InputTag("{}Jets{}".format(prefix, jet_algo_name)),
            secondaryCollectionSrc = cms.InputTag("karmaElectrons"),
        )
    )

    if not options.isData:
        # -- jet-to-gen-jet association map
        from Karma.Common.Producers.JetMatchingProducers_cfi import karmaJetGenJetMatchingProducer
        process.add_module(
            "{}JetGenJetMap{}".format(prefix, jet_algo_name),
            karmaJetGenJetMatchingProducer.clone(
                primaryCollectionSrc = cms.InputTag("{}Jets{}".format(prefix, jet_algo_name)),
                secondaryCollectionSrc = cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),
                maxDeltaR = cms.double(0.4 if 'AK8' in jet_algo_name else 0.2)
            )
        )


def _add_jet_collection_and_dependencies(process, options, prefix, jet_algo_name, suffix, jet_kwargs):
    """convenience function for adding a jet collection and the corresponding METs
    and other related collections to the process"""

    assert jet_algo_name in JET_COLLECTIONS, "Unknown jet collection: {}".format(jet_algo_name)

    _template_jet_collection_name = "{}Jets{}".format(prefix, jet_algo_name)
    _template_met_collection_name = "{}METs{}".format(prefix, jet_algo_name)
    _template_map_names = [
        "{}Jet{}Map{}".format(prefix, _obj_name, jet_algo_name)
        for _obj_name in ('TriggerObject', 'Muon', 'Electron')
    ]

    process.add_module(
        _template_jet_collection_name + suffix,
        getattr(process, _template_jet_collection_name).clone(
            **jet_kwargs
        )
    )
    process.add_module(
        _template_met_collection_name + suffix,
        getattr(process, _template_met_collection_name).clone(
            # jets for type-I correction
            karmaCorrectedJetCollectionSrc=cms.InputTag(
                _template_jet_collection_name + suffix
            ),
        )
    )

    for _template_map_name in _template_map_names:
        process.add_module(
            _template_map_name + suffix,
            getattr(process, _template_map_name).clone(
                primaryCollectionSrc=cms.InputTag(_template_jet_collection_name + suffix),
            )
        )

    if options.isData:
        # data-only

        # -- prefiring Weights
        _template_prefiring_weights_name = "{}PrefiringWeights{}".format(prefix, jet_algo_name)
        process.add_module(
            _template_prefiring_weights_name + suffix,
            getattr(process, _template_prefiring_weights_name).clone(
                karmaJetCollectionSrc = cms.InputTag(_template_jet_collection_name + suffix),
            )
        )
    else:
        # mc-only

        # -- jet-genjet maps
        _template_genjet_map_name = "{}JetGenJetMap{}".format(prefix, jet_algo_name)
        process.add_module(
            _template_genjet_map_name + suffix,
            getattr(process, _template_genjet_map_name).clone(
                primaryCollectionSrc=cms.InputTag(_template_jet_collection_name + suffix),
                secondaryCollectionSrc=cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),
                maxDeltaR=cms.double(0.4 if 'AK8' in jet_algo_name else 0.2)
            )
        )


def _add_all_shifted(process, options, jet_algo_name):
    """convenience function for adding all pipeline-shifted collections to process"""
    assert jet_algo_name in JET_COLLECTIONS, "Unknown jet collection: {}".format(jet_algo_name)

    for _jec_suffix, _jec in JEC_PIPELINES.items():
        _add_jet_collection_and_dependencies(
            process=process,
            options=options,
            prefix="corrected",
            jet_algo_name=jet_algo_name,
            suffix=_jec_suffix,
            jet_kwargs=dict(
                jecUncertaintyShift=cms.double(_jec['shift']),
            )
        )

        if not options.isData:
            for _jer_suffix, _jer in JER_PIPELINES.items():
                _add_jet_collection_and_dependencies(
                    process=process,
                    options=options,
                    prefix="smearedCorrected",
                    jet_algo_name=jet_algo_name,
                    suffix=_jec_suffix+_jer_suffix,
                    jet_kwargs=dict(
                        karmaJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _jec_suffix)),
                        karmaJetGenJetMapSrc = cms.InputTag("correctedJetGenJetMap{}{}".format(jet_algo_name, _jec_suffix)),
                        jerVariation = cms.int32(_jer['variation']),
                    ),
                )

    # jets corrected with one JEC uncertainty source shift
    if False: #if options.doJECUncertaintySources:
        for _unc_source_set_name, _unc_source_set_spec in JEC_UNCERTAINTY_SOURCE_SETS.items():
            assert _unc_source_set_name.endswith('Up') or _unc_source_set_name.endswith('Dn'), \
                "Internal ERROR: _unc_source_set_name should end with 'Up' or 'Dn'"
            _reference_pipeline = "JEC" + ('Up' if _unc_source_set_name.endswith('Up') else "Dn")
            assert _reference_pipeline in JEC_PIPELINES, "Pipeline '{}' needed to construct the JEC uncertainty shifts, but it is missing.".format(_reference_pipeline)
            _add_jet_collection_and_dependencies(
                process=process,
                options=options,
                prefix="uncSourceShifted",
                jet_algo_name=jet_algo_name,
                suffix=_unc_source_set_name,
                jet_kwargs=dict(
                    karmaJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _reference_pipeline)),
                    jetUncertaintySources = cms.vstring(_unc_source_set_spec['sources']),
                    jecUncertaintyShift = cms.double(_unc_source_set_spec['shift']),
                ),
            )


def init_modules(process, options, jet_algo_name):
    '''Configure basic analysis modules. These configurations will be used as templates for
    the pipeline configurations.'''

    # == main collections =================================================

    # -- raw (JEC-uncorrected) valid jets
    from Karma.Common.Producers.CorrectedValidJetsProducer_cfi import karmaCorrectedValidJetsProducer
    process.add_module(
        "rawJets{}".format(jet_algo_name),
        karmaCorrectedValidJetsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaJetCollectionSrc = cms.InputTag("karmaSelectedPatJets{}".format(jet_algo_name)),

            # -- other configuration
            jecFromGlobalTag = cms.bool(options.jecFromGlobalTag),
            jecVersion = "{}/src/JECDatabase/textFiles/{jec_version}_{data_or_mc}/{jec_version}_{data_or_mc}".format(
                os.getenv('CMSSW_BASE'),
                jec_version=options.jecVersion,
                data_or_mc="DATA" if options.isData else "MC",
            ),
            jecAlgoName = cms.string(jet_algo_name.replace('CHS', 'chs')),
            jecLevels = cms.vstring(),
            jecUncertaintyShift = cms.double(0.0),

            # jet ID (for object-based jet ID in PostProcessing using branches 'jet1id', 'jet2id')
            jetIDSpec = cms.string(options.jetIDSpec if options.useObjectBasedJetID else "None"),
            jetIDWorkingPoint = cms.string(options.jetIDWorkingPoint or "None"),

            minJetPt = cms.double(20),
        )
    )

    # -- raw METs

    from Karma.Common.Producers.CorrectedMETsProducer_cfi import karmaCorrectedMETsProducer
    process.add_module(
        "rawMETs{}".format(jet_algo_name),
        karmaCorrectedMETsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaMETCollectionSrc = cms.InputTag("karmaMETs"),

            # jets for type-I correction
            karmaCorrectedJetCollectionSrc = cms.InputTag("rawJets{}".format(jet_algo_name)),

            # -- other configuration
            typeICorrectionMinJetPt = cms.double(15),
            typeICorrectionMaxTotalEMFraction = cms.double(0.9),
        )
    )

    # maps to raw jets
    _add_jet_maps(
        process=process,
        options=options,
        prefix='raw',
        jet_algo_name=jet_algo_name
    )

    # -- JEC-corrected valid jets
    from Karma.Common.Producers.CorrectedValidJetsProducer_cfi import karmaCorrectedValidJetsProducer
    process.add_module(
        "correctedJets{}".format(jet_algo_name),
        karmaCorrectedValidJetsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaJetCollectionSrc = cms.InputTag("karmaSelectedPatJets{}".format(jet_algo_name)),

            # -- other configuration
            jecFromGlobalTag = cms.bool(options.jecFromGlobalTag),
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

            # uncertainty shifts to store in transient maps
            jecUncertaintySources = cms.vstring(_ALL_JEC_UNCERTAINTY_SOURCES if options.doJECUncertaintySources else []),

            # jet ID (for object-based jet ID in PostProcessing using branches 'jet1id', 'jet2id')
            jetIDSpec = cms.string(options.jetIDSpec if options.useObjectBasedJetID else "None"),
            jetIDWorkingPoint = cms.string(options.jetIDWorkingPoint or "None"),

            minJetPt = cms.double(20),
        )
    )

    # -- corrected METs
    from Karma.Common.Producers.CorrectedMETsProducer_cfi import karmaCorrectedMETsProducer
    process.add_module(
        "correctedMETs{}".format(jet_algo_name),
        karmaCorrectedMETsProducer.clone(
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

    _add_jet_maps(
        process=process,
        options=options,
        prefix='corrected',
        jet_algo_name=jet_algo_name
    )

    # -- JEC uncertainty source shifted jets
    from Karma.Common.Producers.JetUncertaintySourceApplier_cfi import karmaJetUncertaintySourceApplier
    process.add_module(
        "uncSourceShiftedJets{}".format(jet_algo_name),
        karmaJetUncertaintySourceApplier.clone(
            # -- input sources
            karmaJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),

            # specify jet uncertainty sources to apply
            jetUncertaintySources = cms.vstring(),
        )
    )

    # -- corrected METs
    from Karma.Common.Producers.CorrectedMETsProducer_cfi import karmaCorrectedMETsProducer
    process.add_module(
        "uncSourceShiftedMETs{}".format(jet_algo_name),
        karmaCorrectedMETsProducer.clone(
            # -- input sources
            karmaEventSrc = cms.InputTag("karmaEvents"),
            karmaMETCollectionSrc = cms.InputTag("karmaMETs"),

            # jets for type-I correction
            karmaCorrectedJetCollectionSrc = cms.InputTag("uncSourceShiftedJets{}".format(jet_algo_name)),

            # -- other configuration
            typeICorrectionMinJetPt = cms.double(15),
            typeICorrectionMaxTotalEMFraction = cms.double(0.9),
        )
    )

    _add_jet_maps(
        process=process,
        options=options,
        prefix='uncSourceShifted',
        jet_algo_name=jet_algo_name
    )

    # == Data-only items =============================================

    # -- prefiring Weights
    from Karma.Common.Producers.PrefiringWeightProducer_cfi import karmaPrefiringWeightProducer
    for _prefix in ('raw', 'corrected', 'uncSourceShifted'):
        process.add_module(
            "{}PrefiringWeights{}".format(_prefix, jet_algo_name),
            karmaPrefiringWeightProducer.clone(
                # -- input sources
                karmaJetCollectionSrc = cms.InputTag("{}Jets{}".format(_prefix, jet_algo_name)),

                # -- other configuration
                prefiringWeightFilePath = cms.string(options.prefiringWeightFilePath),
                prefiringWeightHistName = cms.string(options.prefiringWeightHistName),
                prefiringRateSysUnc = cms.double(0.2),
            )
        )

    # == MC-only main collections =============================================

    if not options.isData:

        # -- JER-smeared valid jets
        from Karma.Common.Producers.SmearedJetsProducer_cfi import karmaSmearedJetsProducer
        process.add_module(
            "smearedCorrectedJets{}".format(jet_algo_name),
            karmaSmearedJetsProducer.clone(
                # -- input sources
                karmaEventSrc = cms.InputTag("karmaEvents"),
                karmaJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
                karmaJetGenJetMapSrc = cms.InputTag("correctedJetGenJetMap{}".format(jet_algo_name)),

                # JER
                jerVersion = "{}/src/JRDatabase/textFiles/{jec_version}_{data_or_mc}/{jec_version}_{data_or_mc}".format(
                    os.getenv('CMSSW_BASE'),
                    jec_version=options.jerVersion,
                    data_or_mc="DATA" if options.isData else "MC",
                ),
                jetAlgoName = cms.string(jet_algo_name.replace('CHS', 'chs')),
                jerVariation = cms.int32(0),  # -1 for 'DOWN', 0 for 'NOMINAL', 1 for 'UP
                jerMethod = cms.string(options.jerMethod)
            )
        )

        # -- JER-smeared METs
        process.add_module(
            "smearedCorrectedMETs{}".format(jet_algo_name),
            getattr(process, "correctedMETs{}".format(jet_algo_name)).clone(
                # jets for type-I correction
                karmaCorrectedJetCollectionSrc=cms.InputTag(
                    "smearedCorrectedJets{}".format(jet_algo_name)
                ),
            )
        )

        _add_jet_maps(
            process=process,
            options=options,
            prefix='smearedCorrected',
            jet_algo_name=jet_algo_name
        )

    # == JEC/JER-shifted collections ==========================================

    _add_all_shifted(process, options, jet_algo_name=jet_algo_name)


def setup_pipeline(process, options, pipeline_name, jet_algo_name, jec_shift=None, jer_variation=None):
    # -- create pipeline modules

    assert jet_algo_name in JET_COLLECTIONS, "Unknown jet collection: {}".format(jet_algo_name)
    assert jec_shift is None or jec_shift in JEC_PIPELINES or jec_shift in JEC_UNCERTAINTY_SOURCE_SETS
    assert jer_variation is None or jer_variation in JER_PIPELINES

    _jet_collection_suffix = (jec_shift or "") + (jer_variation or "")

    print('setup_pipeline{}'.format((pipeline_name, jet_algo_name, _jet_collection_suffix)))

    from Karma.DijetAnalysis.NtupleV2Producer_cfi import dijetNtupleV2Producer

    # use JER-smeared jets in MC
    _cor_prefix = 'corrected'
    if not options.isData:
        _cor_prefix = 'smearedCorrected'

    # use raw jets if no JEC shift requested
    if jec_shift is None:
        assert(jer_variation is None)  # raw JEC + JER variation not supported
        _cor_prefix = "raw"

    # use JEC uncertainty-shifted jets as an input
    if jec_shift in JEC_UNCERTAINTY_SOURCE_SETS:
        assert jer_variation is None, "Applying both JER and JEC uncertainty source shifts is not supported!"
        _cor_prefix = "uncSourceShifted"

    process.add_module(
        "ntuple{}".format(pipeline_name),
        dijetNtupleV2Producer.clone(
            karmaJetCollectionSrc = cms.InputTag("{}Jets{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),
            karmaGenJetCollectionSrc = cms.InputTag("karmaGenJets{}".format(jet_algo_name[:3])),

            karmaJetTriggerObjectMapSrc = cms.InputTag("{}JetTriggerObjectMap{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),
            karmaJetGenJetMapSrc = cms.InputTag("{}JetGenJetMap{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),

            karmaMETCollectionSrc = cms.InputTag("{}METs{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),

            karmaPrefiringWeightSrc = cms.InputTag("{}PrefiringWeights{}{}:nonPrefiringProb".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),
            karmaPrefiringWeightUpSrc = cms.InputTag("{}PrefiringWeights{}{}:nonPrefiringProbUp".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),
            karmaPrefiringWeightDownSrc = cms.InputTag("{}PrefiringWeights{}{}:nonPrefiringProbDown".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)),

            isData = cms.bool(options.isData),
            stitchingWeight = cms.double(options.stitchingWeight),
            npuMeanFile = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_data_zeroBias.txt".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),

            doPrescales = cms.bool(options.doPrescales),  # write out prescales for all trigger paths

            # YAML files specifying analysis binning
            pileupWeightFile = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_ratio_jetHT.root".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),
            pileupWeightFileAlt = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/nPUMean_ratio_zeroBias.root".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),
            pileupWeightByHLTFileBasename = "{}/src/Karma/DijetAnalysis/data/pileup/{YEAR}/byHLT/nPUMean_ratio".format(
                os.getenv('CMSSW_BASE'),
                YEAR="2016",
            ),
            pileupWeightHistogramName = "pileup",

            # jet ID (for event-based jet ID in PostProcessing using branches 'jet1id', 'jet2id')
            jetIDSpec = cms.string(options.jetIDSpec or "None"),
            jetIDWorkingPoint = cms.string(options.jetIDWorkingPoint or "None"),

            # JEC uncertainty shift factors (only for nominal pipeline)
            jesUncertaintySources = cms.VPSet(
                cms.PSet(name=cms.string(_n))
                for _n in _ALL_JEC_UNCERTAINTY_SOURCES
            ) if (options.doJECUncertaintySources and jer_variation is None) else cms.VPSet(),

            # MET filters
            metFilterNames = cms.vstring(
                'Flag_goodVertices',
                'Flag_globalSuperTightHalo2016Filter',
                'Flag_HBHENoiseFilter',
                'Flag_HBHENoiseIsoFilter',
                'Flag_EcalDeadCellTriggerPrimitiveFilter',
                'Flag_BadPFMuonFilter',
                'Flag_eeBadScFilter',
            ),
        )
    )

    # filter ensuring the existence of a leading jet pair
    process.add_module(
        "jetPairFilter{}".format(pipeline_name),
        cms.EDFilter(
            "DijetJetPairFilterV2",
            cms.PSet(
                ntupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
            )
        )
    )

    if options.useHLTFilter:
        # filter ensuring that at least one trigger has fired
        process.add_module(
            "ntupleHLTFilter{}".format(pipeline_name),
            cms.EDFilter(
                "DijetNtupleV2HLTFilter",
                cms.PSet(
                    ntupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                )
            )
        )

    # note: choose to apply these filters in PostProcessing

    ## # filter ensuring that the leading jet is within eta
    ## process.add_module(
    ##     "leadingJetRapidityFilter{}".format(pipeline_name),
    ##     cms.EDFilter(
    ##         "DijetLeadingJetRapidityFilter",
    ##         cms.PSet(
    ##             ntupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
    ##             maxJetAbsRapidity = cms.double(3.0),
    ##         )
    ##     )
    ## )
    ##
    ## # filter ensuring that the leading jet is above pt threshold
    ## process.add_module(
    ##     "leadingJetPtFilter{}".format(pipeline_name),
    ##     cms.EDFilter(
    ##         "DijetLeadingJetPtFilter",
    ##         cms.PSet(
    ##             ntupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
    ##             minJetPt = cms.double(60),
    ##         )
    ##     )
    ## )

    # analyzer for writing out flat ntuple
    process.add_module(
        "pipeline{}".format(pipeline_name),
        cms.EDAnalyzer(
            "DijetNtupleV2FlatOutput",
            cms.PSet(
                isData = cms.bool(options.isData),
                ntupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                treeName = cms.string("Events"),
                checkForCompleteness = cms.bool(options.checkForCompleteness),
            )
        )
    )

    # -- create pipeline sequence

    _pre_ntuple_sequence = cms.Sequence(
        getattr(process, "{}Jets{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)) *
        getattr(process, "{}JetTriggerObjectMap{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)) *
        getattr(process, "{}METs{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix)))

    if options.isData:
        _pre_ntuple_sequence *= getattr(process, "{}PrefiringWeights{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix))

    _post_ntuple_sequence = cms.Sequence(
        getattr(process, "ntuple{}".format(pipeline_name)) *
        getattr(process, "jetPairFilter{}".format(pipeline_name))
    )

    if options.useHLTFilter:
        _post_ntuple_sequence += getattr(process, "ntupleHLTFilter{}".format(pipeline_name))

    # add flat output analyzer
    _post_ntuple_sequence += getattr(process, "pipeline{}".format(pipeline_name))

    _maybe_mc_specific_pre_sequence = cms.Sequence()
    _maybe_mc_specific_post_sequence = cms.Sequence()
    if not options.isData:
        if jec_shift is None:
            # need raw jets and genjet map as smearer input
            _maybe_mc_specific_pre_sequence *= getattr(process, "{}Jets{}".format('raw', jet_algo_name))
            _maybe_mc_specific_pre_sequence *= getattr(process, "{}JetGenJetMap{}".format('raw', jet_algo_name))
        else:
            # need unsmeared jets and genjet map as smearer input
            _maybe_mc_specific_pre_sequence *= getattr(process, "{}Jets{}{}".format('corrected', jet_algo_name, jec_shift))
            _maybe_mc_specific_pre_sequence *= getattr(process, "{}JetGenJetMap{}{}".format('corrected', jet_algo_name, jec_shift))
            # produce genjet map for smeared jets
            _maybe_mc_specific_post_sequence *= getattr(process, "{}JetGenJetMap{}{}".format(_cor_prefix, jet_algo_name, _jet_collection_suffix))

    _complete_pipeline_sequence = cms.Sequence(
        _maybe_mc_specific_pre_sequence *
        _pre_ntuple_sequence *
        _maybe_mc_specific_post_sequence *
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

    # enable the JSON filter (if given)
    if options.jsonFilterFile:
        process.enable_json_lumi_filter(options.jsonFilterFile)

    # -- configure pipelines

    _rng_engines = {}
    for jet_collection in options.jetCollections:
        # create modules with nominal configurations for each jet collection
        init_modules(process, options, jet_algo_name=jet_collection)

        # -- set up pipelines (different for data and MC)

        if options.isData:
            # data -> only add pipelines with JEC shifts (i.e. no JER smearing)
            #for jec_shift in list(JEC_PIPELINES) + (list(JEC_UNCERTAINTY_SOURCE_SETS) if options.doJECUncertaintySources else []):
            for jec_shift in list(JEC_PIPELINES):
                setup_pipeline(
                    process, options,
                    pipeline_name="{}{}".format(jet_collection, jec_shift),
                    jet_algo_name=jet_collection,
                    jec_shift=jec_shift,
                )
                _rng_engines.update({
                    "ntuple{}{}".format(jet_collection, jec_shift) : cms.PSet(
                        initialSeed=cms.untracked.uint32(497931),
                        engineName=cms.untracked.string('TRandom3')
                    )
                })
        else:
            # mc -> add pipelines with both JEC shifts and JER smearing
            #for jec_shift in list(JEC_PIPELINES) + (list(JEC_UNCERTAINTY_SOURCE_SETS) if options.doJECUncertaintySources else []):
            for jec_shift in list(JEC_PIPELINES):
                for jer_variation in JER_PIPELINES:
                    # do not add pipelines with more than one active variation (JER or JEC)
                    if (jer_variation != 'JERNominal' and jec_shift != 'JECNominal'):
                        continue

                    # take pipeline name from active variation (either JER or JEC)
                    _pipeline_suffix = "Nominal"
                    for _suf in (jec_shift, jer_variation):
                        if not _suf.endswith('Nominal'):
                            _pipeline_suffix = _suf
                            break

                    setup_pipeline(
                        process, options,
                        pipeline_name="{}{}".format(jet_collection, _pipeline_suffix),
                        jet_algo_name=jet_collection,
                        jec_shift=jec_shift,
                        jer_variation=jer_variation,
                    )
                    # store config for random number engine (added to service later)
                    _rng_engines.update({
                        # key is name of module that needs the RNG engine
                        "smearedCorrectedJets{}{}{}".format(jet_collection, jec_shift, jer_variation) : cms.PSet(
                            initialSeed=cms.untracked.uint32(83),
                            engineName=cms.untracked.string('TRandom3')
                        ),
                        "ntuple{}{}".format(jet_collection, _pipeline_suffix) : cms.PSet(
                            initialSeed=cms.untracked.uint32(497931),
                            engineName=cms.untracked.string('TRandom3')
                        )
                    })

        # add pipeline without JEC/JER shifts (i.e. raw uncorrected jets)
        if False:
          setup_pipeline(
            process, options,
            pipeline_name="{}{}".format(jet_collection, 'Raw'),
            jet_algo_name=jet_collection,
            jec_shift=None
          )
          _rng_engines.update({
            "ntuple{}{}".format(jet_collection, 'Raw') : cms.PSet(
                initialSeed=cms.untracked.uint32(497931),
                engineName=cms.untracked.string('TRandom3')
            )
          })

    # random number generator service (for JER smearing)
    if _rng_engines:
        process.add_module(
            "RandomNumberGeneratorService",
            cms.Service(
                "RandomNumberGeneratorService",
                **_rng_engines
            )
        )

    # just in case we need it
    return process
