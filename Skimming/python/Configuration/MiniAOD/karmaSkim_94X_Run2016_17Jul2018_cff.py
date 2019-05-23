"""
Karma skim config for 94X miniAOD files
=======================================

This skim config should be used for 2016 samples produced with CMSSW 94X,
e.g. 17Jul2018 Re-MiniAOD or the corresponding Monte-Carlo.

To use:

    # import the module
    from Karma.Skimming.Configuration.MiniAOD import karmaSkim_94X_Run2016_17Jul2018_cff

    # register the options
    options = karmaSkim_94X_Run2016_17Jul2018_cff.register_options(options)

    # configure the process
    karmaSkim_94X_Run2016_17Jul2018_cff.configure(process)


"""
import FWCore.ParameterSet.Config as cms


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
                      default=True,
                      description="If True, only events triggered by a path matching the configured regex will be written out.")
            .register('withPATCollections',
                      type_=bool,
                      default=None,
                      description="Path to JSON file containing certified runs and luminosity blocks.")
    )

def configure(process, options):
    """Apply configuration to a process."""

    # create the main module path
    process.add_path('path')

    # enable the JSON filter (if given)
    if options.jsonFilterFile:
        process.enable_json_lumi_filter(options.jsonFilterFile)

    # == configure CMSSW modules ==========================================

    # -- Jets (default from miniAOD) --------------------------------------

    if options.withPATCollections:
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

    if options.withPATCollections:
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
        ## write out reclustered jets
        #process.add_output_commands('keep patJets_{}_*_*'.format(_jet_collection_name))

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

        # embed jet id information in pat::Jet itprocess
        setattr(
            process,
            _enriched_jet_collection_name,
            cms.EDProducer("PATJetUserDataEmbedder",
                 src = cms.InputTag(_jet_collection_name),
                 userInts = cms.PSet(
                    jetIdWinter16TightLepVeto = cms.InputTag(_id_producer_name),
                 ),
            )
        )

        # add modules to path
        process.path *= getattr(process, _id_producer_name)
        process.path *= getattr(process, _enriched_jet_collection_name)

        # write out ID-enriched jet collection
        if options.withPATCollections:
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

    if options.withPATCollections:
        process.add_output_commands(
            'keep patMETs_slimmedMETs_*_*',
        )

    # -- Electrons --------------------------------------------------------

    # just write out miniAOD electrons
    if options.withPATCollections:
        process.add_output_commands(
            "keep patElectrons_slimmedElectrons_*_*",
        )

    # Note: electron scale/smearing correction information is contained in
    # the following userFloats: 'ecalEnergyPreCorr' and 'ecalEnergyPostCorr'

    # Note: electron ID information is stored as "pseudo-userData" in
    # PAT::Electrons (not in the inherited PAT::Object userData variables)
    # and can be accessed using PAT::Electrons::electronID() with the
    # corresponding tag (e.g. 'cutBasedElectronID-Summer16-80X-V1-loose')


    # -- Muons ------------------------------------------------------------

    # just write out miniAOD muons
    if options.withPATCollections:
        process.add_output_commands(
            "keep patMuons_slimmedMuons_*_*",
        )

    # -- Primary Vertices -------------------------------------------------

    from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

    # "good" primary vertices

    process.add_module(
        'goodOfflinePrimaryVertices',
        cms.EDFilter(
            'PrimaryVertexObjectFilter',
            src = cms.InputTag("offlineSlimmedPrimaryVertices"),
            filterParams = pvSelector.clone(
                maxZ = 24.0
            ),  # ndof >= 4, rho <= 2
        ),
        on_path='path',
        write_out=False,
    )

    # == END configure CMSSW modules ======================================



    # == configure Karma modules ==========================================

    # -- General Event Information ----------------------------------------

    from Karma.Skimming.EventProducer_cfi import karmaEventProducer

    process.add_module(
        'karmaEvents',
        karmaEventProducer(isData=options.isData).clone(
            goodPrimaryVerticesSrc = cms.InputTag("goodOfflinePrimaryVertices"),
        ),
        on_path='path',
        write_out=True,
    )

    # filter out event if no interesting HLT path fired (if requested)
    if options.useHLTFilter:
        process.add_module(
            'karmaEventHLTFilter',
            cms.EDFilter("EventHLTFilter",
                cms.PSet(
                    karmaEventSrc = cms.InputTag("karmaEvents")
                )
            ),
            on_path='path',
            write_out=False, # don't write out the TriggerResults object
        )

    # -- Trigger Objects --------------------------------------------------

    from Karma.Skimming.TriggerObjectCollectionProducer_cfi import karmaTriggerObjectCollectionProducer

    process.add_module(
        'karmaTriggerObjects',
        karmaTriggerObjectCollectionProducer.clone(
            karmaRunSrc = cms.InputTag("karmaEvents"),
        ),
        on_path='path',
        write_out=True,
    )

    # -- MET --------------------------------------------------------------

    from Karma.Skimming.METCollectionProducer_cfi import karmaMETCollectionProducer

    process.add_module(
        'karmaMETs',
        karmaMETCollectionProducer.clone(
            inputCollection = cms.InputTag("slimmedMETs"),
        ),
        on_path='path',
        write_out=True,
    )

    # -- MET correction levels --------------------------------------------

    # note: not included -> all information is already in karma::MET data format

    ## from Karma.Skimming.METCorrectedLVValueMapProducer_cfi import karmaMETCorrectedLVValueMapProducer
    ##
    ## process.add_module(
    ##     'karmaMETCorrectedLVs',
    ##     karmaMETCorrectedLVValueMapProducer.clone(
    ##         inputCollection = cms.InputTag("karmaMETs"),
    ##     ),
    ##     on_path='path',
    ##     write_out=True,
    ## )
    ##
    ## from Karma.Skimming.METCorrectedSumEtValueMapProducer_cfi import karmaMETCorrectedSumEtValueMapProducer
    ##
    ## process.add_module(
    ##     'karmaMETCorrectedSumEts',
    ##     karmaMETCorrectedSumEtValueMapProducer.clone(
    ##         inputCollection = cms.InputTag("karmaMETs"),
    ##     ),
    ##     on_path='path',
    ##     write_out=True,
    ## )

    # -- Jets -------------------------------------------------------------

    from Karma.Skimming.JetCollectionProducer_cfi import karmaJets
    from Karma.Skimming.JetCorrectedLVValueMapProducer_cfi import karmaJetCorrectedLVValueMapProducer, karmaJetCorrectedLVValueMapProducerForPuppi
    from Karma.Skimming.JetIdValueMapProducers_cfi import karmaJetIdValueMapProducer, karmaJetPileupIdValueMapProducer, karmaJetPileupIdDiscriminantValueMapProducer

    # create "karma::Jet" collections from pat::Jets
    for _jet_collection_name in jet_collection_names:

        # add karma modules for producing the skimmed jet collections
        _module_name = "karma{}{}".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
        process.add_module(
            _module_name,
            karmaJets.clone(
                inputCollection = cms.InputTag("{}WithJetIDUserData".format(_jet_collection_name)),
            ),
            on_path='path',
            write_out=True,
        )

        # write out jet ID information to transients (used to fill value maps)
        _t = getattr(process, _module_name).transientInformationSpec
        _t.fromUserIntAsBool = cms.PSet(
            jetIdWinter16TightLepVeto = cms.string("jetIdWinter16TightLepVeto"),
        )
        if 'AK4PFCHS' in _jet_collection_name:
            _t.fromUserFloat = cms.PSet(
                pileupJetId = cms.string("AK4PFCHSpileupJetIdEvaluator:fullDiscriminant"),
            )
            _t.fromUserInt = cms.PSet(
                pileupJetId = cms.string("AK4PFCHSpileupJetIdEvaluator:fullId"),
            )

        # add karma module for producing the Jet ID value map
        _valuemap_module_name = "karma{}{}JetIds".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
        process.add_module(
            _valuemap_module_name,
            karmaJetIdValueMapProducer.clone(
                inputCollection = cms.InputTag(_module_name),
            ),
            on_path='path',
            write_out=True,
        )

        # add karma modules for producing the pileup jet ID value maps (AK4CHS-only)
        if 'AK4PFCHS' in _jet_collection_name:
            _valuemap_module_name = "karma{}{}JetPileupIds".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
            process.add_module(
                _valuemap_module_name,
                karmaJetPileupIdValueMapProducer.clone(
                    inputCollection = cms.InputTag(_module_name),
                ),
                on_path='path',
                write_out=True,
            )
            _valuemap_module_name = "karma{}{}JetPileupIdDiscriminants".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
            process.add_module(
                _valuemap_module_name,
                karmaJetPileupIdDiscriminantValueMapProducer.clone(
                    inputCollection = cms.InputTag(_module_name),
                ),
                on_path='path',
                write_out=True,
            )

        if 'Puppi' in _jet_collection_name:
            _valuemap_producer = karmaJetCorrectedLVValueMapProducerForPuppi
        else:
            _valuemap_producer = karmaJetCorrectedLVValueMapProducer

        # add karma modules for producing the correction level value maps
        _valuemap_module_name = "karma{}{}JECs".format(_jet_collection_name[0].upper(), _jet_collection_name[1:])
        process.add_module(
            _valuemap_module_name,
            _valuemap_producer.clone(
                inputCollection = cms.InputTag(_module_name),
            ),
            on_path='path',
            write_out=True,
        )

    # -- Electrons --------------------------------------------------------

    from Karma.Skimming.ElectronCollectionProducer_cfi import karmaElectronCollectionProducer

    process.add_module(
        'karmaElectrons',
        karmaElectronCollectionProducer.clone(),
        on_path='path',
        write_out=True,
    )

    # -- Electron IDs -----------------------------------------------------

    from Karma.Skimming.ElectronIdValueMapProducer_cfi import karmaElectronIdValueMapProducer

    process.add_module(
        'karmaElectronIds',
        karmaElectronIdValueMapProducer.clone(
            inputCollection = cms.InputTag("karmaElectrons")
        ),
        on_path='path',
        write_out=True
    )

    # -- Muons ------------------------------------------------------------

    from Karma.Skimming.MuonCollectionProducer_cfi import karmaMuonCollectionProducer

    process.add_module(
        'karmaMuons',
        karmaMuonCollectionProducer.clone(),
        on_path='path',
        write_out=True,
    )

    # -- Primary Vertices -------------------------------------------------

    from Karma.Skimming.VertexCollectionProducer_cfi import karmaVertexCollectionProducer

    process.add_module(
        'karmaVertices',
        karmaVertexCollectionProducer.clone(),
        on_path='path',
        write_out=True,

    )

    # == END configure Karma modules ======================================


    # selective writeout based on path decisions
    process.enable_selective_writeout('path')

    # just in case we need it
    return process
