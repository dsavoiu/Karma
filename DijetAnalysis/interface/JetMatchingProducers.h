#pragma once

// system include files
#include <memory>

#include "Math/VectorUtil.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "Karma/Common/interface/Producers/GenericMatchingProducer.h"
#include "Karma/Common/interface/Tools/Matchers.h"

// -- output data formats
#include "DataFormats/Common/interface/Ref.h"
#include "DataFormats/Common/interface/AssociationMap.h"

// -- input data formats
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"


//
// class declaration
//
namespace dijet {

    // -- matchers

    typedef karma::DeltaRThresholdMatcher<karma::JetCollection, karma::TriggerObjectCollection> JetTriggerObjectMatcher;
    typedef karma::DeltaRThresholdMatcher<karma::JetCollection, karma::MuonCollection> JetMuonMatcher;
    typedef karma::DeltaRThresholdMatcher<karma::JetCollection, karma::ElectronCollection> JetElectronMatcher;
    typedef karma::LowestDeltaRMatcher<karma::JetCollection, karma::LVCollection> JetLVMatcher;

    // -- main producers

    // jet-to-trigger-object matching producer
    class JetTriggerObjectMatchingProducer :
        public karma::GenericMatchingProducer<
            karma::JetCollection,
            karma::TriggerObjectCollection,
            JetTriggerObjectMatcher,
            edm::OneToMany<karma::JetCollection, karma::TriggerObjectCollection>> {

      public:
        explicit JetTriggerObjectMatchingProducer(const edm::ParameterSet& config) :
            karma::GenericMatchingProducer<
                karma::JetCollection,
                karma::TriggerObjectCollection,
                JetTriggerObjectMatcher,
                edm::OneToMany<karma::JetCollection, karma::TriggerObjectCollection>>(config, config.getParameter<double>("maxDeltaR")) {};
        virtual ~JetTriggerObjectMatchingProducer() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    };

    // jet-to-muon matching producer
    class JetMuonMatchingProducer :
        public karma::GenericMatchingProducer<
            karma::JetCollection,
            karma::MuonCollection,
            JetMuonMatcher,
            edm::OneToMany<karma::JetCollection, karma::MuonCollection>> {

      public:
        explicit JetMuonMatchingProducer(const edm::ParameterSet& config) :
            karma::GenericMatchingProducer<
                karma::JetCollection,
                karma::MuonCollection,
                JetMuonMatcher,
                edm::OneToMany<karma::JetCollection, karma::MuonCollection>>(config, config.getParameter<double>("maxDeltaR")) {};
        virtual ~JetMuonMatchingProducer() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    };

    // jet-to-electron matching producer
    class JetElectronMatchingProducer :
        public karma::GenericMatchingProducer<
            karma::JetCollection,
            karma::ElectronCollection,
            JetElectronMatcher,
            edm::OneToMany<karma::JetCollection, karma::ElectronCollection>> {

      public:
        explicit JetElectronMatchingProducer(const edm::ParameterSet& config) :
            karma::GenericMatchingProducer<
                karma::JetCollection,
                karma::ElectronCollection,
                JetElectronMatcher,
                edm::OneToMany<karma::JetCollection, karma::ElectronCollection>>(config, config.getParameter<double>("maxDeltaR")) {};
        virtual ~JetElectronMatchingProducer() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    };

    // jet-to-LV matching producer (for e.g. gen-jets)
    class JetLVMatchingProducer :
        public karma::GenericMatchingProducer<
            karma::JetCollection,
            karma::LVCollection,
            JetLVMatcher,
            edm::OneToMany<karma::JetCollection, karma::LVCollection>> {

      public:
        explicit JetLVMatchingProducer(const edm::ParameterSet& config) :
            karma::GenericMatchingProducer<
                karma::JetCollection,
                karma::LVCollection,
                JetLVMatcher,
                edm::OneToMany<karma::JetCollection, karma::LVCollection>>(config, config.getParameter<double>("maxDeltaR")) {};
        virtual ~JetLVMatchingProducer() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    };

}  // end namespace
