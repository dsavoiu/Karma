#pragma once

// system include files
#include <memory>

#include "Math/VectorUtil.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/makeRefToBaseProdFrom.h"

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

    // matcher

    typedef karma::LowestDeltaRMatcher<karma::JetCollection, karma::LVCollection> JetGenJetMatcher;

    // -- main producer

    class JetGenJetMatchingProducer :
        public karma::GenericMatchingProducer<
            karma::JetCollection,
            karma::LVCollection,
            JetGenJetMatcher> {

      public:
        explicit JetGenJetMatchingProducer(const edm::ParameterSet& config) :
            karma::GenericMatchingProducer<
                karma::JetCollection,
                karma::LVCollection,
                JetGenJetMatcher>(config, config.getParameter<double>("maxDeltaR")) {};
        virtual ~JetGenJetMatchingProducer() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

      private:

        // ----------member data ---------------------------

    };
}  // end namespace
