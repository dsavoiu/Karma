#!/usr/bin/env python
import os

import FWCore.ParameterSet.Config as cms

from JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer
from JetGenJetMatchingProducer_cfi import dijetJetGenJetMatchingProducer
from CorrectedValidJetsProducer_cfi import dijetCorrectedValidJetsProducer
from CorrectedMETsProducer_cfi import dijetCorrectedMETsProducer
from NtupleProducer_cfi import dijetNtupleProducer


class DijetAnalysis:
    """Helper class. Defines an interface for setting up a CMSSW process for running the dijet analysis."""

    def __init__(self, process, is_data):
        self._is_data = is_data
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
                #jetIDSpec = cms.string("None"),   # use "None" for no object-based JetID
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

        if not self._is_data:
            setattr(
                self._process,
                "jetGenJetMap{}".format(jet_algo_name),
                dijetJetGenJetMatchingProducer.clone(
                    dijetEventSrc = cms.InputTag("dijetEvents"),
                    dijetJetCollectionSrc = cms.InputTag("correctedJets{}".format(jet_algo_name)),
                    dijetGenJetCollectionSrc = cms.InputTag("dijetGenJets{}".format(jet_algo_name[:3])),
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

            if not self._is_data:
                setattr(
                    self._process,
                    "jetGenJetMap{}{}".format(jet_algo_name, _suffix),
                    dijetJetGenJetMatchingProducer.clone(
                        dijetEventSrc = cms.InputTag("dijetEvents"),
                        dijetJetCollectionSrc = cms.InputTag("correctedJets{}{}".format(jet_algo_name, _suffix)),
                        dijetGenJetCollectionSrc = cms.InputTag("dijetGenJets{}".format(jet_algo_name[:3])),
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
                dijetGenJetCollectionSrc = cms.InputTag("dijetGenJets{}".format(jet_algo_name[:3])),

                dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)),
                dijetJetGenJetMapSrc = cms.InputTag("jetGenJetMap{}{}".format(jet_algo_name, jet_collection_suffix)),

                dijetMETCollectionSrc = cms.InputTag("correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)),
                #dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),  # no Type-I correction

                isData = cms.bool(self._is_data),
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
                    isData = cms.bool(self._is_data),
                    dijetNtupleSrc = cms.InputTag("ntuple{}".format(pipeline_name)),
                    dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}".format(pipeline_name)),
                    #outputFileName = cms.string("output_flat.root"),  # deprecated: using TFileService instead
                    treeName = cms.string("Events"),
                    checkForCompleteness = cms.bool(False),
                )
            )
        )
        if self._is_data:
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
        else:
            self._pipeline_sequences[pipeline_name] = cms.Sequence(
                getattr(self._process, "correctedJets{}{}".format(jet_algo_name, jet_collection_suffix)) *
                getattr(self._process, "jetTriggerObjectMap{}{}".format(jet_algo_name, jet_collection_suffix)) *
                getattr(self._process, "correctedMETs{}{}".format(jet_algo_name, jet_collection_suffix)) *
                getattr(self._process, "jetGenJetMap{}{}".format(jet_algo_name, jet_collection_suffix)) *
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
